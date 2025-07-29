# result_collector.py
from typing import List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ConfigDict

from dtx.config import globals
from dtx.core.engine.evaluator import EvaluatorRouter
from dtx.core.engine.scanner import EngineConfig, MultiTurnScanner
from dtx_models.analysis import RedTeamPlan
from dtx_models.results import EvalReport
from dtx_models.tactic import PromptMutationTactic
from dtx.plugins.providers.base.agent import BaseAgent

from dtx_models.analysis import PromptDataset
from .planner import PlanInput

from dtx.cli.scoping import ScopeInput, RedTeamScopeCreator
from dtx.cli.planner import RedTeamPlanGenerator
from dtx.cli.providers import ProviderFactory
from dtx.cli.console_output import BaseResultCollector

from dtx_models.evaluator import EvaluatorInScope

class TestRunInput(BaseModel):
    agent_type: str
    url: Optional[str] = ""
    max_prompts: int = 1000000
    override_tactics: List[str] = Field(default_factory=list)


class RedTeamTestRunner:
    def __init__(self, config: TestRunInput):
        self.config = config
        self.report: Optional[EvalReport] = None

    def run(
        self, plan: RedTeamPlan, agent: BaseAgent, collector: BaseResultCollector
    ) -> EvalReport:
        scope = plan.scope

        tactics = [
            PromptMutationTactic(name=t) for t in self.config.override_tactics
        ] or scope.redteam.tactics

        # Get the global evaluator from red team plan
        if scope.redteam.global_evaluator:
            global_evaluator = scope.redteam.global_evaluator.evaluation_method
        else:
            preferred_evaluator = agent.get_preferred_evaluator()
            if preferred_evaluator:
                global_evaluator = preferred_evaluator.evaluation_method
            else:
                global_evaluator = None

        config = EngineConfig(
            evaluator_router=EvaluatorRouter(
                model_eval_factory=globals.get_eval_factory()
            ),
            test_suites=plan.test_suites,
            tactics_repo=globals.get_tactics_repo(),
            tactics=tactics,
            global_evaluator=global_evaluator,
            max_per_tactic=scope.redteam.max_prompts_per_tactic,
        )

        scanner = MultiTurnScanner(config)

        for result in scanner.scan(agent, max_prompts=self.config.max_prompts):
            collector.add_result(result)

        collector.finalize()

        self.report = EvalReport(
            scope=plan.scope,
            eval_results=collector.results if hasattr(collector, "results") else [],
        )
        return self.report

    def save_yaml(self, path: str):
        if not self.report:
            raise ValueError("Run must be called before saving.")
        yaml_data = yaml.dump(self.report.model_dump(), default_flow_style=False)
        with open(path, "w") as file:
            file.write(yaml_data)

    def save_json(self, path: str):
        if not self.report:
            raise ValueError("Run must be called before saving.")
        json_data = self.report.model_dump_json(indent=2)
        with open(path, "w") as file:
            file.write(json_data)


class QuickRedteamRunnerInput(BaseModel):
    plan_file: Optional[str]
    max_prompts: int
    prompts_per_risk: int
    agent: Optional[str]
    url: str
    output: bool
    yml_file: str
    json_file: str
    tactics: List[str]
    dataset: PromptDataset
    evaluator: Optional[EvaluatorInScope]
    collector: Union[BaseResultCollector]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class QuickRedteamRunner:
    def __init__(self, input: QuickRedteamRunnerInput):
        self.input = input

    def run(self):
        plan = self._load_or_generate_plan(
            plan_file=self.input.plan_file,
            max_prompts=self.input.max_prompts,
            prompts_per_risk=self.input.prompts_per_risk,
        )

        agent_type, url = self._resolve_agent_and_url(plan)

        agent = ProviderFactory().get_agent(plan.scope, agent_type, url)

        runner = RedTeamTestRunner(
            TestRunInput(
                agent_type=agent_type,
                url=url,
                max_prompts=self.input.max_prompts,
                override_tactics=self.input.tactics or [],
            )
        )

        runner.run(plan=plan, agent=agent, collector=self.input.collector)

        if self.input.output:
            runner.save_yaml(self.input.yml)
            runner.save_json(self.input.json_file)
        else:
            print("Skipping file output. Use -o or --output to enable saving.")

    def _resolve_agent_and_url(self, plan):
        if self.input.agent:
            return self.input.agent, self.input.url

        if plan.scope.providers:
            provider = plan.scope.providers[0]
            agent_type = provider.provider
            url = getattr(provider.config, "model", getattr(provider.config, "url", ""))
            print(f"Using provider from plan: agent={agent_type}, url={url}")
            return agent_type, url

        raise ValueError("No agent specified. Use --agent or provide a plan file with provider information.")

    def _load_or_generate_plan(self, plan_file, max_prompts, prompts_per_risk):
        if plan_file:
            return RedTeamPlanGenerator.load_yaml(plan_file)

        scope = self._create_scope()
        plan_config = PlanInput(dataset=self.input.dataset, max_prompts=max_prompts, prompts_per_risk=prompts_per_risk)
        return RedTeamPlanGenerator(scope=scope, config=plan_config).run()

    def _create_scope(self):
        scope_config = ScopeInput(description="Generated during run")
        scope = RedTeamScopeCreator(scope_config).run()
        if self.input.evaluator:
            scope.redteam.global_evaluator = self.input.evaluator
        return scope
