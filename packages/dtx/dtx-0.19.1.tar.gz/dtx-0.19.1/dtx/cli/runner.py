from typing import List, Optional

import yaml
from pydantic import BaseModel, ConfigDict

from dtx.config import globals
from dtx.core.engine.evaluator import EvaluatorRouter
from dtx.core.engine.scanner import EngineConfig, MultiTurnScanner
from dtx_models.analysis import RedTeamPlan, PromptDataset
from dtx_models.results import EvalReport
from dtx_models.tactic import PromptMutationTactic
from dtx_models.evaluator import EvaluatorInScope
from dtx.plugins.providers.base.agent import BaseAgent

from dtx.cli.scoping import ScopeInput, RedTeamScopeCreator
from dtx.cli.planner import PlanInput, RedTeamPlanGenerator
from dtx.cli.providers import ProviderFactory
from dtx.cli.console_output import BaseResultCollector


# -------------------------
# Main test runner (plan-driven)
# -------------------------
class RedTeamTestRunner:
    def __init__(self):
        self.report: Optional[EvalReport] = None

    def run(
        self,
        plan: RedTeamPlan,
        agent: BaseAgent,
        collector: BaseResultCollector,
        override_tactics: Optional[List[PromptMutationTactic]] = None,
        max_prompts: Optional[int] = None,
    ) -> EvalReport:
        scope = plan.scope
        tactics = override_tactics or scope.redteam.tactics

        global_evaluator = (
            scope.redteam.global_evaluator.evaluation_method
            if scope.redteam.global_evaluator
            else agent.get_preferred_evaluator().evaluation_method
            if agent.get_preferred_evaluator()
            else None
        )

        engine_config = EngineConfig(
            evaluator_router=EvaluatorRouter(model_eval_factory=globals.get_eval_factory()),
            test_suites=plan.test_suites,
            tactics_repo=globals.get_tactics_repo(),
            tactics=tactics,
            global_evaluator=global_evaluator,
            max_per_tactic=scope.redteam.max_prompts_per_tactic,
        )

        scanner = MultiTurnScanner(engine_config)
        for result in scanner.scan(agent, max_prompts=max_prompts or scope.redteam.max_prompts):
            collector.add_result(result)

        collector.finalize()

        self.report = EvalReport(
            scope=scope,
            eval_results=getattr(collector, "results", []),
        )
        return self.report

    def save_yaml(self, path: str):
        if not self.report:
            raise ValueError("Run must be called before saving.")
        with open(path, "w") as file:
            yaml.dump(self.report.model_dump(), file, default_flow_style=False)

    def save_json(self, path: str):
        if not self.report:
            raise ValueError("Run must be called before saving.")
        with open(path, "w") as file:
            file.write(self.report.model_dump_json(indent=2))


# -------------------------
# CLI-driven runner input
# -------------------------
class QuickRedteamRunnerInput(BaseModel):
    plan_file: Optional[str]
    max_prompts: int
    prompts_per_risk: int
    agent: Optional[str]
    url: Optional[str]
    output: bool
    yml_file: str
    json_file: str
    dataset: PromptDataset
    tactics: Optional[List[PromptMutationTactic]] = None
    evaluator: Optional[EvaluatorInScope] = None
    collector: Optional[BaseResultCollector] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def set_tactics_by_name(self, names: List[str]):
        self.tactics = [PromptMutationTactic(name=n) for n in names]


# -------------------------
# CLI runner class
# -------------------------
class QuickRedteamRunner:
    def __init__(self, input: QuickRedteamRunnerInput):
        self.input = input

    def run(self):
        plan = self._load_or_generate_plan()

        agent_type, url = self._resolve_agent_and_url(plan)
        agent = ProviderFactory().get_agent(plan.scope, agent_type, url)

        runner = RedTeamTestRunner()
        runner.run(
            plan=plan,
            agent=agent,
            collector=self.input.collector,
            override_tactics=self.input.tactics,
            max_prompts=self.input.max_prompts,
        )

        if self.input.output:
            runner.save_yaml(self.input.yml_file)
            runner.save_json(self.input.json_file)
        else:
            print("Skipping file output. Use -o or --output to enable saving.")

    def _load_or_generate_plan(self) -> RedTeamPlan:
        if self.input.plan_file:
            return RedTeamPlanGenerator.load_yaml(self.input.plan_file)

        scope = self._create_scope()
        plan_config = PlanInput(
            dataset=self.input.dataset,
            max_prompts=self.input.max_prompts,
            prompts_per_risk=self.input.prompts_per_risk,
        )
        return RedTeamPlanGenerator(scope=scope, config=plan_config).run()

    def _create_scope(self):
        scope = RedTeamScopeCreator(ScopeInput(description="Generated during run")).run()
        if self.input.evaluator:
            scope.redteam.global_evaluator = self.input.evaluator
        return scope

    def _resolve_agent_and_url(self, plan: RedTeamPlan):
        if self.input.agent:
            return self.input.agent, self.input.url or ""

        if plan.scope.providers:
            provider = plan.scope.providers[0]
            agent_type = provider.provider
            url = getattr(provider.config, "model", getattr(provider.config, "url", ""))
            print(f"Using provider from plan: agent={agent_type}, url={url}")
            return agent_type, url

        raise ValueError("No agent provided and no providers found in plan.")
