import logging
import os
import shutil
from pathlib import Path

import filelock
from django.conf import settings
from django.test import TestCase

from documents.models import Document
from documents.sanity_checker import check_sanity, SanityCheckMessages
from documents.tests.utils import DirectoriesMixin


class TestSanityCheckMessages(TestCase):
    def test_no_messages(self):
        messages = SanityCheckMessages()
        self.assertEqual(len(messages), 0)
        self.assertFalse(messages.has_error())
        self.assertFalse(messages.has_warning())
        with self.assertLogs() as capture:
            messages.log_messages()
            self.assertEqual(len(capture.output), 1)
            self.assertEqual(capture.records[0].levelno, logging.INFO)
            self.assertEqual(
                capture.records[0].message, "Sanity checker detected no issues."
            )

    def test_info(self):
        messages = SanityCheckMessages()
        messages.info("Something might be wrong")
        self.assertEqual(len(messages), 1)
        self.assertFalse(messages.has_error())
        self.assertFalse(messages.has_warning())
        with self.assertLogs() as capture:
            messages.log_messages()
            self.assertEqual(len(capture.output), 1)
            self.assertEqual(capture.records[0].levelno, logging.INFO)
            self.assertEqual(capture.records[0].message, "Something might be wrong")

    def test_warning(self):
        messages = SanityCheckMessages()
        messages.warning("Something is wrong")
        self.assertEqual(len(messages), 1)
        self.assertFalse(messages.has_error())
        self.assertTrue(messages.has_warning())
        with self.assertLogs() as capture:
            messages.log_messages()
            self.assertEqual(len(capture.output), 1)
            self.assertEqual(capture.records[0].levelno, logging.WARNING)
            self.assertEqual(capture.records[0].message, "Something is wrong")

    def test_error(self):
        messages = SanityCheckMessages()
        messages.error("Something is seriously wrong")
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages.has_error())
        self.assertFalse(messages.has_warning())
        with self.assertLogs() as capture:
            messages.log_messages()
            self.assertEqual(len(capture.output), 1)
            self.assertEqual(capture.records[0].levelno, logging.ERROR)
            self.assertEqual(capture.records[0].message, "Something is seriously wrong")


class TestSanityCheck(DirectoriesMixin, TestCase):
    def make_test_data(self):

        with filelock.FileLock(settings.MEDIA_LOCK):
            # just make sure that the lockfile is present.
            shutil.copy(
                os.path.join(
                    os.path.dirname(__file__),
                    "samples",
                    "documents",
                    "originals",
                    "0000001.pdf",
                ),
                os.path.join(self.dirs.originals_dir, "0000001.pdf"),
            )
            shutil.copy(
                os.path.join(
                    os.path.dirname(__file__),
                    "samples",
                    "documents",
                    "archive",
                    "0000001.pdf",
                ),
                os.path.join(self.dirs.archive_dir, "0000001.pdf"),
            )
            shutil.copy(
                os.path.join(
                    os.path.dirname(__file__),
                    "samples",
                    "documents",
                    "thumbnails",
                    "0000001.png",
                ),
                os.path.join(self.dirs.thumbnail_dir, "0000001.png"),
            )

        return Document.objects.create(
            title="test",
            checksum="42995833e01aea9b3edee44bbfdd7ce1",
            archive_checksum="62acb0bcbfbcaa62ca6ad3668e4e404b",
            content="test",
            pk=1,
            filename="0000001.pdf",
            mime_type="application/pdf",
            archive_filename="0000001.pdf",
        )

    def assertSanityError(self, messageRegex):
        messages = check_sanity()
        self.assertTrue(messages.has_error())
        self.assertRegex(messages[0]["message"], messageRegex)

    def test_no_docs(self):
        self.assertEqual(len(check_sanity()), 0)

    def test_success(self):
        self.make_test_data()
        self.assertEqual(len(check_sanity()), 0)

    def test_no_thumbnail(self):
        doc = self.make_test_data()
        os.remove(doc.thumbnail_path)
        self.assertSanityError("Thumbnail of document .* does not exist")

    def test_thumbnail_no_access(self):
        doc = self.make_test_data()
        os.chmod(doc.thumbnail_path, 0o000)
        self.assertSanityError("Cannot read thumbnail file of document")
        os.chmod(doc.thumbnail_path, 0o777)

    def test_no_original(self):
        doc = self.make_test_data()
        os.remove(doc.source_path)
        self.assertSanityError("Original of document .* does not exist.")

    def test_original_no_access(self):
        doc = self.make_test_data()
        os.chmod(doc.source_path, 0o000)
        self.assertSanityError("Cannot read original file of document")
        os.chmod(doc.source_path, 0o777)

    def test_original_checksum_mismatch(self):
        doc = self.make_test_data()
        doc.checksum = "WOW"
        doc.save()
        self.assertSanityError("Checksum mismatch of document")

    def test_no_archive(self):
        doc = self.make_test_data()
        os.remove(doc.archive_path)
        self.assertSanityError("Archived version of document .* does not exist.")

    def test_archive_no_access(self):
        doc = self.make_test_data()
        os.chmod(doc.archive_path, 0o000)
        self.assertSanityError("Cannot read archive file of document")
        os.chmod(doc.archive_path, 0o777)

    def test_archive_checksum_mismatch(self):
        doc = self.make_test_data()
        doc.archive_checksum = "WOW"
        doc.save()
        self.assertSanityError("Checksum mismatch of archived document")

    def test_empty_content(self):
        doc = self.make_test_data()
        doc.content = ""
        doc.save()
        messages = check_sanity()
        self.assertFalse(messages.has_error())
        self.assertFalse(messages.has_warning())
        self.assertEqual(len(messages), 1)
        self.assertRegex(messages[0]["message"], "Document .* has no content.")

    def test_orphaned_file(self):
        doc = self.make_test_data()
        Path(self.dirs.originals_dir, "orphaned").touch()
        messages = check_sanity()
        self.assertFalse(messages.has_error())
        self.assertTrue(messages.has_warning())
        self.assertEqual(len(messages), 1)
        self.assertRegex(messages[0]["message"], "Orphaned file in media dir")

    def test_archive_filename_no_checksum(self):
        doc = self.make_test_data()
        doc.archive_checksum = None
        doc.save()
        self.assertSanityError("has an archive file, but its checksum is missing.")

    def test_archive_checksum_no_filename(self):
        doc = self.make_test_data()
        doc.archive_filename = None
        doc.save()
        self.assertSanityError("has an archive file checksum, but no archive filename.")
