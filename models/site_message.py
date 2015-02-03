
SM_ERROR, SM_VALIDATION_FAIL, SM_SUCCESS, SM_NOTIFY = "SM_ERROR", "SM_VALIDATION_FAIL", "SM_SUCCESS", "SM_NOTIFY"

class SiteMessage(object):

    def __init__(self, message, intent=None):

        """
        :param message:
        :param intent:
        :return:

        message can start with !, ? or * for intent.

         e.g. "!OMG the webserver is on fire."
         "*Your order has been submitted successfully."

        """

        self.message = message

        if intent is None:

            if message[0] == "!":
                self.message_intent = SM_ERROR
                self.message = message[1:]
            elif message[0] == "?":
                self.message_intent = SM_VALIDATION_FAIL
                self.message = message[1:]
            elif message[0] == "*":
                self.message_intent = SM_SUCCESS
                self.message = message[1:]
            else:
                self.message_intent = SM_NOTIFY

        else:
            self.message_intent = intent

        self._format_for_display()

    def _format_for_display(self):

        if self.message_intent == 'SM_SUCCESS':
            site_msg_icon = "fa-check-circle"
            site_msg_css_class = "site-message-success"
        elif self.message_intent == 'SM_VALIDATION_FAIL':
            site_msg_icon = "fa-question-circle"
            site_msg_css_class = "site-message-validation"
        elif self.message_intent == 'SM_ERROR':
            site_msg_icon = "fa-exclamation-triangle"
            site_msg_css_class = "site-message-error"
        else:
            site_msg_icon = "fa-circle-o"
            site_msg_css_class = "site-message-info"

        self.icon = site_msg_icon
        self.css_class = site_msg_css_class





