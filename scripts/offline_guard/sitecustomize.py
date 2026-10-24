"""Installed before unittest discovery by the release shell entry point."""
import os
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]

def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto','socket.sendmsg'):
        raise PermissionError('release: network forbidden')
    if event in ('open','os.listdir','os.scandir') and args and isinstance(args[0],(str,bytes,os.PathLike)):
        p=Path(os.fsdecode(args[0])).absolute()
        if p.name in ('.env','compute.env') or p.name.endswith('.local.json'):
            raise PermissionError('release: credentials forbidden')
        if p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if rel.startswith(('docs/runner/exp002','runs/exp002')) or rel=='ops/budget_ledger.jsonl':
                raise PermissionError('release: held-out access forbidden')
    if event=='subprocess.Popen' and any('ollama' in str(x).lower() for x in args[:2]):
        raise PermissionError('release: inference server forbidden')
sys.addaudithook(guard)
_original_run=unittest.TestCase.run

def scoped_run(self,result=None):
    if self.id()=='tests.analysis.test_readiness.ReadinessTests.test_real_frozen_manifest_contract_without_outcomes':
        result=result or self.defaultTestResult()
        result.startTest(self)
        result.addSkip(self,'REL-001a prohibits reading real EXP-002 manifest; owner/controller must run separately')
        result.stopTest(self)
        return result
    return _original_run(self,result)
unittest.TestCase.run=scoped_run
