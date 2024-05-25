
class BasePageLayout:

    def __init__(self):
        pass

    def page_content(self):
        raise NotImplementedError

    def display_page(self):
        self.page_content()
