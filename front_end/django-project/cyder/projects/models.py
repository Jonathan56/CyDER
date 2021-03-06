from django.db import models
from cyder.models.models import Model
import json
from celery.result import AsyncResult
import sim_worker.celery
import sim_worker.tasks
import pandas

class ProjectException(Exception):
    pass

# NOTE REGARDING PROJECT EDITIONS:
#     Once simulations have been launched for a given project, if this project is edited, 
#     the previous simulation rusults will not be ovewritten and will still be displayed on the results page.
#     To obtain only new results, a new project must created.
#     It is probably wise in the next developments to make sure that on edition of an already simulated project, 
#     all "SimulationResult" model intances associated to the "Project" model instance are deleted.

class Project(models.Model):
    name = models.CharField(max_length=50)
    task_id = models.TextField(default="null")
    stage = models.CharField(max_length=20, default="Modification")
    status = models.CharField(max_length=20, default="NA")
    settings = models.TextField(default="null")
    config = models.TextField(default="null")
    config_detail = models.TextField(default="null")
    results = models.TextField(default="null")
    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.old_settings = self.settings

    def save(self, *args, **kwargs):
        if self.old_settings != self.settings:
            self.old_settings = self.settings
            self.stage = "Modification"
            self.status = "NA"
        super(Project, self).save(*args, **kwargs)

    def quickSave(self, *args, **kwargs):
        if self.old_settings != self.settings:
            self.old_settings = self.settings
        super(Project, self).save(*args, **kwargs)


    def revoke(self):
        task = AsyncResult(self.task_id, app=sim_worker.celery.app)
        task.revoke(terminate=True)
        task.forget()
        if self.stage == "Configuration":
            self.stage = "Modification"
            self.status = "NA"
        elif self.stage == "Detail Configuration":
            self.stage = "Modification"
            self.status = "NA"
        elif self.stage == "Simulation":
            self.stage = "Configuration"
            self.status = "Success"
        self.save()

    def run_config(self):
        if self.status == "Started" or self.status == "Pending":
            raise ProjectException("Can't configure a project when it is currently in " + self.stage)
        task = sim_worker.tasks.run_configuration.delay(self.id, json.loads(self.settings))
        tasks = []
        tasks.append(task.id) 
        self.task_id=json.dumps(tasks)
        self.stage = "Configuration"
        self.status = "Pending"
        self.save()

    def run_detailed_config(self):
        if self.status == "Started" or self.status == "Pending":
            raise ProjectException("Can't configure a project when it is currently in " + self.stage)
        task = sim_worker.tasks.run_detailed_configuration.delay(self.id, json.loads(self.settings))
        tasks = []
        tasks.append(task.id) 
        self.task_id=json.dumps(tasks)
        self.stage = "Detail Configuration"
        self.status = "Pending"
        self.save()


    def run_sim(self):
        if self.status == "Started" or self.status == "Pending":
            raise ProjectException("Can't run a simulation on a project when it is currently in " + self.stage)
        if self.stage != "Simulation" and (not ((self.stage == "Configuration" or self.stage == "Detail Configuration") and self.status == "Success")):
            raise ProjectException("A successful configuration must be performed before running a simulation")
        settings=json.loads(self.settings)
        days=settings['simDaysList']
        tasks=[]
        for day in days:
            task = sim_worker.tasks.run_simulation.delay(self.id, settings, day)
            tasks.append(task.id)
        tasks=json.dumps(tasks)
        self.task_id=tasks
        self.stage = "Simulation"
        self.status = "Pending"
        self.save()

class SimulationResult(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.CharField(max_length=70, blank=True)
    date = models.CharField(max_length=70, blank=True)
    results = models.TextField(default="null")

class ComponentResult(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    component = models.CharField(max_length=70, blank=True)
    results = models.TextField(default="null")
