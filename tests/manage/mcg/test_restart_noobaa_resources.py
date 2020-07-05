import logging
import pytest

from ocs_ci.framework.testlib import (
    ManageTest, tier4, tier4a, ignore_leftover_label
)
from ocs_ci.ocs.resources import pod
from ocs_ci.ocs import constants, defaults, exceptions
from ocs_ci.ocs.resources.mcg import MCG


log = logging.getLogger(__name__)


@tier4
@tier4a
@ignore_leftover_label(constants.drain_canary_pod_label)
@pytest.mark.parametrize(
    argnames=["resource_to_delete"],
    argvalues=[
        pytest.param(
            *['noobaa_core'], marks=pytest.mark.polarion_id("OCS-XXX")
        ),
        pytest.param(
            *['noobaa_db'], marks=pytest.mark.polarion_id("OCS-XXX")
        )
    ]
)
class TestRestartNoobaaResources(ManageTest):
    """
    Test Noobaa resources restart and check Noobaa health

    """
    @pytest.fixture(scope='class', autouse=True)
    def setup(self):
        self.mcg_obj = MCG()

    def test_restart_noobaa_resources(self, resource_to_delete):
        """
        Test Noobaa resources restart and check Noobaa health

        """
        labels_map = {
            'noobaa_core': constants.NOOBAA_CORE_POD_LABEL,
            'noobaa_db': constants.NOOBAA_DB_LABEL
        }
        pod_obj = self.resource_obj = pod.Pod(
            **pod.get_pods_having_label(
                label=labels_map[resource_to_delete],
                namespace=defaults.ROOK_CLUSTER_NAMESPACE
            )[0]
        )

        pod_obj.delete(force=True)
        assert pod_obj.ocp.wait_for_resource(
            condition='Running', selector=self.selector,
            resource_count=1, timeout=300
        )

        # check noobaa health
        if not self.mcg_obj.status:
            raise exceptions.NoobaaHealthException("Cluster health is NOT OK")
