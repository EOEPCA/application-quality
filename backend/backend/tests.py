from django.test import TestCase
from backend.models import Pipeline, Subworkflow, CommandLineTool
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class PipelineModelTest(TestCase):
    def test_str_representation(self):
        pipeline = Pipeline.objects.create(
            name="TestPipeline",
            template="cwl:CommandLineTool"
        )
        self.assertEqual(str(pipeline), "TestPipeline")


class SubworkflowModelTest(TestCase):
    def test_str_representation(self):
        tool = CommandLineTool.objects.create(
            slug="tool1",
            name="Tool 1",
            definition="...",
            version="1.0"
        )
        subworkflow = Subworkflow.objects.create(
            slug="sw1",
            name="Subworkflow 1",
            pipeline_step="step",
            definition="def",
            version="1.0",
        )
        subworkflow.tools.add(tool)
        self.assertEqual(str(tool), "Tool 1")
        self.assertEqual(str(subworkflow), "Subworkflow 1")


class PipelineViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass"
        )
        self.client = APIClient()
        self.token = self.get_token()

    def get_token(self):
        response = self.client.post("/api/token/",{"username": "testuser", "password": "pass"})
        return response.data["access"]

    def test_pipeline_create_unauthenticated_fail(self):
        url = "/api/pipelines/"
        data = {
            "name": "Dummy",
            "description": "Dummy pipeline",
            "version": "0.1",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_pipeline_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        url = "/api/pipelines/"
        data = {
            "name": "Dummy",
            "description": "Dummy pipeline",
            "version": "0.1",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Pipeline.objects.count(), 1)

    def test_pipeline_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        Pipeline.objects.create(
            name="Pipeline1",
            template="foo",
            owner=self.user
        )
        response = self.client.get("/api/pipelines/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Pipeline1")


class PipelineRunViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="runner",
            password="pass"
        )
        self.pipeline = Pipeline.objects.create(
            name="PipelineTest",
            template="cwl",
            owner=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_pipeline_run_invalid_pipeline(self):
        url = "/api/pipelines/999/runs/"
        response = self.client.post(url, {"parameters": {}}, format="json")
        self.assertEqual(response.status_code, 404)

    # def test_create_pipeline_run_valid(self):
    #     url = f"/api/pipelines/{self.pipeline.id}/runs/"
    #     response = self.client.post(url, {"parameters": {}}, format='json')
    #     self.assertEqual(response.status_code, 201)
    #     self.assertTrue(PipelineRun.objects.exists())
