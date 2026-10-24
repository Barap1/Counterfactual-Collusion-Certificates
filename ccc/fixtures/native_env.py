"""Native replay plugin: prescribed tasks/costs with unmodified Jira semantics.

Loaded only explicitly through environment.import_path. Config is private
harness state; neither labels nor policy instructions are rendered into prompts.
"""

from copy import deepcopy

from envs.dcops.jira_ticket.jira_ticket_env import JiraTicketEnvironment


class MechanismJiraEnvironment(JiraTicketEnvironment):
    tools_environment_name = "JiraTicketEnvironment"

    def _build_tasks(self, max_tasks):
        tasks=deepcopy(self.env_config["fixture_data"]["tasks"])
        notice=self.env_config["fixture_data"].get("public_notice","")
        if notice:
            for task in tasks:
                if task in notice:
                    tasks[task]["priority"]="critical"
        return tasks

    def _build_agents(self, num_agents):
        names = list(self.env_config["fixture_data"]["agent_names"])
        return names, {a: {"availability": 8.0, "skills": {"review": 1.0}} for a in names}

    def _compute_costs(self):
        return deepcopy(self.env_config["fixture_data"]["costs"])

    def get_network_context(self):
        return super().get_network_context() + self.env_config["fixture_data"].get("public_notice", "")
