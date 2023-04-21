from uuid import uuid4

import jsonschema
import numpy as np
import pytest

from prefect.server.schemas.actions import (
    BlockTypeUpdate,
    DeploymentCreate,
    DeploymentUpdate,
    FlowRunCreate,
)


@pytest.mark.parametrize(
    "test_params,expected_dict",
    [
        ({"param": 1}, {"param": 1}),
        ({"param": "1"}, {"param": "1"}),
        ({"param": {1: 2}}, {"param": {"1": 2}}),
        (
            {"df": {"col": {0: "1"}}},
            {"df": {"col": {"0": "1"}}},
        ),  # Example of serialized dataframe parameter with int key
        (
            {"df": {"col": {0: np.float64(1.0)}}},
            {"df": {"col": {"0": 1.0}}},
        ),  # Example of serialized dataframe parameter with numpy value
    ],
)
class TestFlowRunCreate:
    def test_dict_json_compatible_succeeds_with_parameters(
        self, test_params, expected_dict
    ):
        frc = FlowRunCreate(flow_id=uuid4(), flow_version="0.1", parameters=test_params)
        res = frc.dict(json_compatible=True)
        assert res["parameters"] == expected_dict


class TestDeploymentCreate:
    def test_create_with_worker_pool_queue_id_warns(self):
        with pytest.warns(
            UserWarning,
            match=(
                "`worker_pool_queue_id` is no longer supported for creating "
                "deployments. Please use `work_pool_name` and "
                "`work_queue_name` instead."
            ),
        ):
            deployment_create = DeploymentCreate(
                **dict(name="test-deployment", worker_pool_queue_id=uuid4())
            )

        assert getattr(deployment_create, "worker_pool_queue_id", 0) == 0

    @pytest.mark.parametrize(
        "kwargs",
        [
            ({"worker_pool_queue_name": "test-worker-pool-queue"}),
            ({"work_pool_queue_name": "test-work-pool-queue"}),
            ({"worker_pool_name": "test-worker-pool"}),
        ],
    )
    def test_create_with_worker_pool_name_warns(self, kwargs):
        with pytest.warns(
            UserWarning,
            match=(
                "`worker_pool_name`, `worker_pool_queue_name`, and "
                "`work_pool_name` are"
                "no longer supported for creating "
                "deployments. Please use `work_pool_name` and "
                "`work_queue_name` instead."
            ),
        ):
            deployment_create = DeploymentCreate(
                **dict(name="test-deployment", **kwargs)
            )

        for key in kwargs.keys():
            assert getattr(deployment_create, key, 0) == 0

    def test_check_valid_configuration_removes_required_if_defaults_exist(self):
        # This should fail because my-field is required but has no default
        deployment_create = DeploymentCreate(
            name="test-deployment",
            infra_overrides={},
        )

        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                    },
                },
            }
        }
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            deployment_create.check_valid_configuration(base_job_template)
        assert excinfo.value.message == "'my-field' is a required property"

        # This should pass because the value has a default
        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                        "default": "my-default-for-my-field",
                    },
                },
            }
        }
        deployment_create.check_valid_configuration(base_job_template)

        # make sure the required fields are still there
        assert "my-field" in base_job_template["variables"]["required"]

        # This should also pass
        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                        "default": "my-default-for-my-field",
                    },
                },
            }
        }
        deployment_create = DeploymentUpdate(
            infra_overrides={"my_field": "my_value"},
        )
        deployment_create.check_valid_configuration(base_job_template)


class TestDeploymentUpdate:
    def test_update_with_worker_pool_queue_id_warns(self):
        with pytest.warns(
            UserWarning,
            match=(
                "`worker_pool_queue_id` is no longer supported for updating "
                "deployments. Please use `work_pool_name` and "
                "`work_queue_name` instead."
            ),
        ):
            deployment_update = DeploymentUpdate(**dict(worker_pool_queue_id=uuid4()))

        assert getattr(deployment_update, "worker_pool_queue_id", 0) == 0

    @pytest.mark.parametrize(
        "kwargs",
        [
            ({"worker_pool_queue_name": "test-worker-pool-queue"}),
            ({"work_pool_queue_name": "test-work-pool-queue"}),
            ({"worker_pool_name": "test-worker-pool"}),
        ],
    )
    def test_update_with_worker_pool_name_warns(self, kwargs):
        with pytest.warns(
            UserWarning,
            match=(
                "`worker_pool_name`, `worker_pool_queue_name`, and "
                "`work_pool_name` are"
                "no longer supported for creating "
                "deployments. Please use `work_pool_name` and "
                "`work_queue_name` instead."
            ),
        ):
            deployment_update = DeploymentCreate(**kwargs)

        for key in kwargs.keys():
            assert getattr(deployment_update, key, 0) == 0

    def test_check_valid_configuration_removes_required_if_defaults_exist(self):
        # This should fail because my-field is required but has no default
        deployment_update = DeploymentUpdate(
            infra_overrides={},
        )

        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                    },
                },
            }
        }
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            deployment_update.check_valid_configuration(base_job_template)
        assert excinfo.value.message == "'my-field' is a required property"

        # This should pass because the value has a default
        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                        "default": "my-default-for-my-field",
                    },
                },
            }
        }
        deployment_update.check_valid_configuration(base_job_template)

        # make sure the required fields are still there
        assert "my-field" in base_job_template["variables"]["required"]

        # This should also pass
        base_job_template = {
            "variables": {
                "type": "object",
                "required": ["my-field"],
                "properties": {
                    "my-field": {
                        "type": "string",
                        "title": "My Field",
                        "default": "my-default-for-my-field",
                    },
                },
            }
        }
        deployment_update = DeploymentUpdate(
            infra_overrides={"my_field": "my_value"},
        )
        deployment_update.check_valid_configuration(base_job_template)


class TestBlockTypeUpdate:
    def test_updatable_fields(self):
        fields = BlockTypeUpdate.updatable_fields()
        assert fields == {
            "logo_url",
            "documentation_url",
            "description",
            "code_example",
        }
