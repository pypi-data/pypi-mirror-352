class StfAssertionError(AssertionError):
    def __init__(self, screenshot, console_log):
        self.screenshot = screenshot
        self:console_log = console_log