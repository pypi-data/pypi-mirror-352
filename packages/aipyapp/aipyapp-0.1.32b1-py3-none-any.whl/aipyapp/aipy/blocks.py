#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from pathlib import Path
from collections import OrderedDict

from loguru import logger

from .libmcp import extract_call_tool

class CodeBlocks:
    def __init__(self, console):
        self.console = console
        self.blocks = OrderedDict()
        self.code_pattern = re.compile(
            r'<!--\s*Block-Start:\s*(\{.*?\})\s*-->\s*```(\w+)?\s*\n(.*?)\n```\s*<!--\s*Block-End:\s*(\{.*?\})\s*-->',
            re.DOTALL
        )
        self.line_pattern = re.compile(
            r'<!--\s*Cmd-(\w+):\s*(\{.*?\})\s*-->'
        )
        self.log = logger.bind(src='code_blocks')

    def save_block(self, block):
        if block and block.get('filename'):
            path = Path(block['filename'])
            try:
                #TODO: path check
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(block['content'], encoding='utf-8')
            except Exception as e:
                self.log.error("Failed to save file", filename=block['filename'], reason=e)

    def parse(self, markdown_text, parse_mcp=False):
        blocks = OrderedDict()
        errors = []
        for match in self.code_pattern.finditer(markdown_text):
            start_json, lang, content, end_json = match.groups()
            try:
                start_meta = json.loads(start_json)
                end_meta = json.loads(end_json)
            except json.JSONDecodeError as e:
                self.console.print_exception(show_locals=True)
                error = {'JSONDecodeError': {'json_str': start_json, 'reason': str(e)}}
                errors.append(error)
                continue

            code_id = start_meta.get("id")
            if code_id != end_meta.get("id"):
                self.log.error("Start and end id mismatch", start_id=code_id, end_id=end_meta.get("id"))
                error = {'Start and end id mismatch': {'start_id': code_id, 'end_id': end_meta.get("id")}}
                errors.append(error)
                continue

            if code_id in blocks or code_id in self.blocks:
                self.log.error("Duplicate code id", code_id=code_id)
                error = {'Duplicate code id': {'code_id': code_id}}
                errors.append(error)
                continue

            block = {
                'language': lang,
                'content': content,
                'base_id': start_meta.get('base_id'),
                'filename': start_meta.get('filename')
            }
            blocks[code_id] = block
            self.log.info("Parsed code block", code_id=code_id, filename=block['filename'])
            self.save_block(block)

        self.blocks.update(blocks)

        exec_ids = []
        line_matches = self.line_pattern.findall(markdown_text)
        for line_match in line_matches:
            cmd, json_str = line_match
            try:
                line_meta = json.loads(json_str)
            except json.JSONDecodeError as e:
                self.log.error("Invalid JSON in Cmd-{cmd} block", json_str=json_str, reason=e)
                error = {f'Invalid JSON in Cmd-{cmd} block': {'json_str': json_str, 'reason': str(e)}}
                errors.append(error)
                continue

            error = None
            if cmd == 'Exec':
                exec_id = line_meta.get("id")
                if not exec_id:
                    error = {'Cmd-Exec block without id': {'json_str': json_str}}
                elif exec_id not in self.blocks:
                    error = {'Cmd-Exec block not found': {'exec_id': exec_id}}
                else:
                    exec_ids.append(exec_id)
            else:
                error = {f'Unknown command in Cmd-{cmd} block': {'cmd': cmd}}

            if error:
                errors.append(error)

        ret = {}
        if errors: ret['errors'] = errors
        if exec_ids: ret['exec_ids'] = exec_ids
        if blocks: ret['blocks'] = {k: {'language': v['language'], 'filename': v['filename']} for k, v in blocks.items()}
        
        if parse_mcp and not blocks:
            json_content = extract_call_tool(markdown_text)
            if json_content:
                ret['call_tool'] = json_content
                self.log.info("Parsed MCP call_tool", json_content=json_content)

        return ret
    
    def get_code_by_id(self, code_id):
        try:
            return self.blocks[code_id]['content']
        except KeyError:
            self.log.error("Code id not found", code_id=code_id)
            self.console.print("❌ Code id not found", code_id=code_id)
            return None
        
    def get_block_by_id(self, code_id):
        try:
            return self.blocks[code_id]
        except KeyError:
            self.log.error("Code id not found", code_id=code_id)
            self.console.print("❌ Code id not found", code_id=code_id)
            return None