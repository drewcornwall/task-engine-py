class PlanReporter:
    def __init__(self):
        pass

    def report(self, plan: list[str]):
        raise NotImplementedError


plan_reporters = []


def register_plan_reporter(cls):
    """Decorator to register a plan reporter class"""
    plan_reporters.append(cls())
    return cls


@register_plan_reporter
class ConsolePlanReporter(PlanReporter):
    def report(self, plan: list[str]):
        separator = " -> "
        print("\033[1;32mPlan : " + separator.join(plan) + "\033[0m")