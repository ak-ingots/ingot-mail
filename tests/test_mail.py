import pickle
import unittest

from ingot_mail.mail import Mail, MailDeliveryError, MailError, MailHeaderError


class MailTestCase(unittest.TestCase):
    def test_the_repr_tells_no_address_nor_text(self) -> None:
        mail = Mail(to=("al@b.c",), subject="Your code", text="123456", sender="h@b.c")
        self.assertEqual(repr(mail), "Mail(subject='Your code')")

    def test_a_mail_with_headers_hides_them_and_is_hashed_without(self) -> None:
        mail = Mail(to=("al@b.c",), subject="Hi", text="", headers={"X-A": "1"})
        self.assertEqual(repr(mail), "Mail(subject='Hi')")
        self.assertEqual(hash(mail), hash(Mail(to=("al@b.c",), subject="Hi", text="")))


class ErrorsTestCase(unittest.TestCase):
    def test_a_header_error_names_its_header(self) -> None:
        error = MailHeaderError.for_header("subject")
        self.assertIsInstance(error, MailError)
        self.assertIsInstance(error, ValueError)
        self.assertEqual(error.header, "subject")
        self.assertEqual(str(error), "a header unfit to send: subject")

    def test_a_delivery_error_tells_if_transient(self) -> None:
        error = MailDeliveryError.for_reason("timeout", is_transient=True)
        self.assertIsInstance(error, MailError)
        self.assertEqual(error.reason, "timeout")
        self.assertTrue(error.is_transient)
        self.assertEqual(str(error), "a mail not delivered: timeout")

    def test_the_errors_survive_pickling(self) -> None:
        for error in (
            MailHeaderError.for_header("to"),
            MailDeliveryError.for_reason("550 no such user", is_transient=False),
        ):
            with self.subTest(error=error):
                copy = pickle.loads(pickle.dumps(error))
                self.assertIs(type(copy), type(error))
                self.assertEqual(copy.args, error.args)
