# -*- coding: utf-8 -*-

from blitzdb import Document
from blitzdb.fields import (BooleanField,
                            CharField,
                            DateTimeField,
                            ForeignKeyField,
                            ManyToManyField,
                            TextField,
                            EnumField,
                            IntegerField)

import os
import uuid
import time
import datetime
import logging
import traceback

from checkmate.helpers.hashing import Hasher
from checkmate.lib.stats.helpers import directory_splitter
from checkmate.lib.analysis import AnalyzerSettingsError
from checkmate.helpers.issue import IssuesMapReducer

try:
    from sqlalchemy.sql import (select,
                                insert,
                                func,
                                and_,
                                expression,
                                exists)
except ImportError:
    pass

logger = logging.getLogger(__name__)

class BaseDocument(Document):

    __abstract__ = True

    created_at = DateTimeField(auto_now_add=True, indexed=True)
    updated_at = DateTimeField(auto_now=True, indexed=True)

    def before_save(self):
        if not 'created_at' in self:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    def before_update(self, set_fields, unset_fields):
        self.updated_at = datetime.datetime.now()
        set_fields['updated_at'] = self.updated_at

class IssueCategory(BaseDocument):

    name = CharField(indexed=True, unique=True, length=50)

class IssueClass(BaseDocument):

    class Severity:
        critical = 1
        potential_bug = 2
        minor = 3
        recommendation = 4

    hash = CharField(indexed=True, length=64)
    title = CharField(indexed=True, length=100)
    analyzer = CharField(indexed=True, length=50)
    language = CharField(indexed=True, length=50)
    code = CharField(indexed=True, length=50)
    description = TextField(indexed=False)

    occurrence_description = CharField(indexed=True, length=2000)

    severity = IntegerField(indexed=True)
    categories = ManyToManyField('IssueCategory')

    class Meta(BaseDocument.Meta):
        unique_together = (('code', 'analyzer'),)

class IssueOccurrence(BaseDocument):

    hash = CharField(indexed=True, length=64)
    file_revision = ForeignKeyField(
        'FileRevision', backref='issue_occurrences')
    issue = ForeignKeyField('Issue', backref='issue_occurrences')
    from_row = IntegerField()
    to_row = IntegerField()
    from_column = IntegerField()
    to_column = IntegerField()
    sequence = IntegerField(default=0)

class Issue(BaseDocument):

    class IgnoreReason:
        not_specified = 0
        not_relevant = 1
        false_positive = 2

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    project = ForeignKeyField('Project', backref='issues', nullable=False)
    analyzer = CharField(indexed=True, length=100, nullable=False)
    code = CharField(indexed=True, length=100, nullable=False)
    fingerprint = CharField(indexed=True, length=255, nullable=False)

    ignore = BooleanField(indexed=True, default=False, nullable=False)
    ignore_reason = IntegerField(indexed=True, nullable=True)
    ignore_comment = CharField(indexed=False, length=255, nullable=True)

    class Meta(Document.Meta):
        unique_together = [('project', 'fingerprint', 'analyzer', 'code')]
        dbref_includes = ['code', 'analyzer']

class MockFileRevision(BaseDocument):

    __abstract__ = True

    def get_file_content(self):
        return self.code

class FileRevision(BaseDocument):

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    project = ForeignKeyField('Project')
    path = CharField(indexed=True, length=2000)
    language = CharField(indexed=True, length=50)
    sha = CharField(indexed=True, length=64)
    dependencies = ManyToManyField(
        'FileRevision', backref='dependent_file_revisions')

    class Meta(Document.Meta):
        collection = "filerevision"

    def get_file_content(self):
        if hasattr(self, '_file_content'):
            if callable(self._file_content):
                return self._file_content()
            return self._file_content
        raise NotImplementedError

class Diff(BaseDocument):

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    project = ForeignKeyField('Project', backref='diffs')
    snapshot_a = ForeignKeyField('Snapshot', backref='diffs_a')
    snapshot_b = ForeignKeyField('Snapshot', backref='diffs_b')

    def summarize_issues(self, include_filename=False, ignore=False):
        # Placeholder for non-FileBackend summarization
        return {
            "added": [],
            "fixed": []
        }

class DiffIssueOccurrence(BaseDocument):

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    diff = ForeignKeyField('Diff', backref='issue_occurrences')
    issue_occurrence = ForeignKeyField(
        'IssueOccurrence', backref='diff_issue_occurrences')
    key = EnumField(enums=('added', 'fixed'))

class DiffFileRevision(BaseDocument):

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    diff = ForeignKeyField('Diff', backref='file_revisions')
    file_revision = ForeignKeyField('FileRevision', backref='diffs')
    key = EnumField(enums=('added', 'deleted', 'modified'))

class Snapshot(BaseDocument):

    hash = CharField(indexed=True, length=64)
    configuration = CharField(indexed=True, length=64)
    project = ForeignKeyField('Project')
    file_revisions = ManyToManyField('FileRevision', backref='snapshots')
    analyzed = BooleanField(indexed=True)

    class Meta(Document.Meta):
        pass

    def summarize_issues(self, include_filename=False, ignore=False):
        # Placeholder for non-FileBackend summarization
        return {
            "issues": []
        }

class ProjectIssueClass(BaseDocument):

    project = ForeignKeyField('Project', backref='project_issue_classes')
    issue_class = ForeignKeyField(
        'IssueClass', backref='project_issue_classes')
    enabled = BooleanField(default=True)

    class Meta(BaseDocument.Meta):
        unique_together = (('project', 'issue_class'),)

class Project(BaseDocument):

    IssueClass = IssueClass
    project_id = IntegerField(indexed=True, unique=True)

    configuration = CharField(indexed=True, length=64)

    class Meta(Document.Meta):
        collection = "project"

    @property
    def settings(self):
        return self.get('settings', {})

    def get_issue_classes(self, backend=None, enabled=True, sort=None, **kwargs):
        # Simplified logic without FileBackend
        query = {'project_issue_classes.project': self}
        if enabled is not None:
            query['project_issue_classes.enabled'] = enabled

        issue_classes = []  # Replace with backend-independent logic

        return issue_classes

    def get_issues_data(self, backend=None, extra_fields=None):

        if extra_fields is None:
            extra_fields = []

        grouped_issue_data = {}

        # Simplified placeholder logic for issues data retrieval
        return grouped_issue_data

