#!/usr/bin/env python3
"""
TMDL (Tabular Model Definition Language) Formatter and Validator

This script validates and formats TMDL files according to Microsoft's official specification.
Reference: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview

TMDL Format Rules:
1. Objects are declared using: object_type object_name
2. Properties use colon delimiter: propertyName: value
3. Expressions use equals delimiter: measure Name = EXPRESSION
4. Indentation uses TABS (not spaces) - default single tab between levels
5. Multi-line expressions are indented one level deeper than parent properties
6. Triple backticks (```) can wrap expressions to preserve whitespace

Usage:
    python tmdl_formatter.py validate <path>    # Validate TMDL files
    python tmdl_formatter.py format <path>      # Format TMDL files
    python tmdl_formatter.py check <path>       # Check without modifying

Author: Power BI Development Team
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class TmdlTokenType(Enum):
    """Token types in TMDL"""
    OBJECT_DECLARATION = "OBJECT_DECLARATION"
    PROPERTY = "PROPERTY"
    EXPRESSION = "EXPRESSION"
    MULTI_LINE_START = "MULTI_LINE_START"
    MULTI_LINE_END = "MULTI_LINE_END"
    COMMENT = "COMMENT"
    BLANK = "BLANK"
    CONTINUATION = "CONTINUATION"


@dataclass
class TmdlToken:
    """Represents a parsed TMDL token"""
    type: TmdlTokenType
    content: str
    line_number: int
    indent_level: int = 0
    raw_indent: str = ""


@dataclass
class ValidationError:
    """Represents a TMDL validation error"""
    file_path: str
    line_number: int
    message: str
    severity: str = "error"  # error, warning, info
    
    def __str__(self):
        return f"{self.file_path}:{self.line_number} [{self.severity}] {self.message}"


@dataclass
class TmdlFile:
    """Represents a parsed TMDL file"""
    path: str
    tokens: List[TmdlToken] = field(default_factory=list)
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)


# TMDL Object Types (based on TOM hierarchy)
TMDL_OBJECT_TYPES = {
    # Database-level
    "database", "model", "dataSource", "table", "relationship",
    "role", "expression", "culture", "perspective",
    # Table-level
    "column", "measure", "hierarchy", "partition", "annotation",
    # Hierarchy-level
    "level",
    # Column types
    "calculatedColumn", "calculatedTableColumn", "dataColumn",
    # Partition types  
    "mPartition", "calculatedPartition", "entityPartition",
    # Relationship
    "singleColumnRelationship",
    # Other
    "tablePermission", "ref", "parameter"
}

# Properties that can have multi-line values
MULTI_LINE_PROPERTIES = {
    "expression", "formatString", "description", "sourceExpression",
    "filterExpression", "detailRowsExpression", "defaultDetailRowsExpression"
}


class TmdlParser:
    """Parser for TMDL files"""
    
    def __init__(self):
        self.current_file: Optional[TmdlFile] = None
        self.in_multiline: bool = False
        self.multiline_indent: int = 0
        
    def parse_file(self, file_path: str) -> TmdlFile:
        """Parse a TMDL file and return structured tokens"""
        self.current_file = TmdlFile(path=file_path)
        self.in_multiline = False
        self.multiline_indent = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.current_file.errors.append(
                ValidationError(file_path, 0, f"Cannot read file: {e}")
            )
            return self.current_file
        
        for line_num, line in enumerate(lines, 1):
            token = self._parse_line(line, line_num)
            self.current_file.tokens.append(token)
        
        return self.current_file
    
    def _parse_line(self, line: str, line_num: int) -> TmdlToken:
        """Parse a single line into a token"""
        # Get raw content without trailing newline
        content = line.rstrip('\n\r')
        
        # Calculate indent
        stripped = content.lstrip('\t')
        indent_level = len(content) - len(stripped)
        raw_indent = content[:indent_level]
        
        # Empty/blank line
        if not stripped or stripped.isspace():
            return TmdlToken(
                type=TmdlTokenType.BLANK,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Comment line (starts with //)
        if stripped.startswith('//'):
            return TmdlToken(
                type=TmdlTokenType.COMMENT,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Triple backtick delimiter
        if stripped.strip() == '```':
            self.in_multiline = not self.in_multiline
            return TmdlToken(
                type=TmdlTokenType.MULTI_LINE_START if self.in_multiline else TmdlTokenType.MULTI_LINE_END,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )

        # Multi-line block opening on the same line as a property/expression, e.g.:
        #   source = ```
        #   expression = ```
        # This is common in Power BI / TMDL exports.
        if not self.in_multiline:
            s = stripped.strip()
            if s.endswith('```') and s != '```':
                self.in_multiline = True
                return TmdlToken(
                    type=TmdlTokenType.MULTI_LINE_START,
                    content=content,
                    line_number=line_num,
                    indent_level=indent_level,
                    raw_indent=raw_indent
                )
        
        # Inside multi-line block
        if self.in_multiline:
            return TmdlToken(
                type=TmdlTokenType.CONTINUATION,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Object declaration (object_type object_name)
        first_word = stripped.split()[0] if stripped.split() else ""
        if first_word.lower() in TMDL_OBJECT_TYPES:
            return TmdlToken(
                type=TmdlTokenType.OBJECT_DECLARATION,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Expression (uses = delimiter)
        if '=' in stripped and not ':' in stripped.split('=')[0]:
            return TmdlToken(
                type=TmdlTokenType.EXPRESSION,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Property (uses : delimiter)
        if ':' in stripped:
            return TmdlToken(
                type=TmdlTokenType.PROPERTY,
                content=content,
                line_number=line_num,
                indent_level=indent_level,
                raw_indent=raw_indent
            )
        
        # Continuation of previous line
        return TmdlToken(
            type=TmdlTokenType.CONTINUATION,
            content=content,
            line_number=line_num,
            indent_level=indent_level,
            raw_indent=raw_indent
        )


class TmdlValidator:
    """Validator for TMDL files"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        
    def validate(self, tmdl_file: TmdlFile) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate a parsed TMDL file"""
        self.errors = []
        self.warnings = []
        
        self._validate_indent_consistency(tmdl_file)
        self._validate_object_structure(tmdl_file)
        self._validate_property_syntax(tmdl_file)
        self._validate_expression_syntax(tmdl_file)
        self._validate_multiline_blocks(tmdl_file)
        
        return self.errors, self.warnings
    
    def _validate_indent_consistency(self, tmdl_file: TmdlFile):
        """Check for consistent indentation (should use tabs, not spaces)"""
        for token in tmdl_file.tokens:
            if token.type == TmdlTokenType.BLANK:
                continue
                
            # Check for space indentation
            content = token.content
            if content.startswith(' ') and not content.startswith('\t'):
                # Count leading spaces
                space_count = len(content) - len(content.lstrip(' '))
                if space_count > 0:
                    self.warnings.append(ValidationError(
                        tmdl_file.path,
                        token.line_number,
                        f"Line uses spaces for indentation ({space_count} spaces). TMDL recommends tabs.",
                        severity="warning"
                    ))
    
    def _validate_object_structure(self, tmdl_file: TmdlFile):
        """Validate object declaration structure"""
        indent_stack = []
        
        for token in tmdl_file.tokens:
            if token.type == TmdlTokenType.BLANK or token.type == TmdlTokenType.COMMENT:
                continue
                
            if token.type == TmdlTokenType.OBJECT_DECLARATION:
                # Check proper indent level
                if indent_stack:
                    expected_indent = indent_stack[-1] + 1
                    if token.indent_level < expected_indent - 1:
                        # Popping back up the stack
                        while indent_stack and token.indent_level <= indent_stack[-1]:
                            indent_stack.pop()
                    
                indent_stack.append(token.indent_level)
    
    def _validate_property_syntax(self, tmdl_file: TmdlFile):
        """Validate property syntax"""
        for token in tmdl_file.tokens:
            if token.type == TmdlTokenType.PROPERTY:
                content = token.content.strip()
                if ':' in content:
                    parts = content.split(':', 1)
                    prop_name = parts[0].strip()
                    
                    # Property name should not have spaces
                    if ' ' in prop_name:
                        self.errors.append(ValidationError(
                            tmdl_file.path,
                            token.line_number,
                            f"Property name '{prop_name}' should not contain spaces"
                        ))
    
    def _validate_expression_syntax(self, tmdl_file: TmdlFile):
        """Validate expression/measure syntax"""
        for i, token in enumerate(tmdl_file.tokens):
            if token.type == TmdlTokenType.EXPRESSION:
                content = token.content.strip()
                
                # Check for proper measure/column expression format
                if content.startswith(('measure ', 'calculatedColumn ')):
                    if '=' not in content:
                        self.errors.append(ValidationError(
                            tmdl_file.path,
                            token.line_number,
                            "Expression object must have '=' followed by DAX expression"
                        ))
    
    def _validate_multiline_blocks(self, tmdl_file: TmdlFile):
        """Validate multi-line block structure"""
        in_multiline = False
        multiline_start = 0
        
        for token in tmdl_file.tokens:
            if token.type == TmdlTokenType.MULTI_LINE_START:
                if in_multiline:
                    self.errors.append(ValidationError(
                        tmdl_file.path,
                        token.line_number,
                        "Nested multi-line blocks (```) are not allowed"
                    ))
                in_multiline = True
                multiline_start = token.line_number
            elif token.type == TmdlTokenType.MULTI_LINE_END:
                if not in_multiline:
                    self.errors.append(ValidationError(
                        tmdl_file.path,
                        token.line_number,
                        "Unexpected closing multi-line delimiter (```)"
                    ))
                in_multiline = False
        
        if in_multiline:
            self.errors.append(ValidationError(
                tmdl_file.path,
                multiline_start,
                "Multi-line block opened but never closed"
            ))


class TmdlFormatter:
    """Formatter for TMDL files"""
    
    def __init__(self, use_tabs: bool = True, tab_size: int = 4):
        self.use_tabs = use_tabs
        self.tab_size = tab_size
        self.indent_char = '\t' if use_tabs else ' ' * tab_size
        
    def format_file(self, tmdl_file: TmdlFile) -> str:
        """Format a TMDL file and return the formatted content"""
        formatted_lines = []
        
        for token in tmdl_file.tokens:
            formatted_line = self._format_token(token)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def _format_token(self, token: TmdlToken) -> str:
        """Format a single token"""
        if token.type == TmdlTokenType.BLANK:
            return ""
        
        # Preserve comment indentation
        if token.type == TmdlTokenType.COMMENT:
            return self._normalize_indent(token.content, token.indent_level)
        
        # Format based on token type
        content = token.content.strip()
        indent = self.indent_char * token.indent_level
        
        return f"{indent}{content}"
    
    def _normalize_indent(self, content: str, expected_level: int) -> str:
        """Normalize indentation to use consistent characters"""
        stripped = content.lstrip('\t ')
        return f"{self.indent_char * expected_level}{stripped}"
    
    def convert_spaces_to_tabs(self, content: str) -> str:
        """Convert space indentation to tab indentation"""
        lines = content.split('\n')
        converted = []
        
        for line in lines:
            if not line.strip():
                converted.append(line)
                continue
            
            # Count leading spaces
            stripped = line.lstrip(' ')
            space_count = len(line) - len(stripped)
            
            if space_count > 0:
                # Convert to tabs (assuming 4 spaces = 1 tab)
                tab_count = space_count // self.tab_size
                remaining_spaces = space_count % self.tab_size
                new_indent = '\t' * tab_count + ' ' * remaining_spaces
                converted.append(f"{new_indent}{stripped}")
            else:
                converted.append(line)
        
        return '\n'.join(converted)


def find_tmdl_files(path: str, recursive: bool = True) -> List[str]:
    """Find all TMDL files in a directory"""
    path_obj = Path(path)
    tmdl_files = []
    
    if path_obj.is_file():
        if path_obj.suffix.lower() in ['.tmdl', '.tmd']:
            return [str(path_obj)]
        return []
    
    if path_obj.is_dir():
        pattern = '**/*.tmdl' if recursive else '*.tmdl'
        tmdl_files.extend(str(p) for p in path_obj.glob(pattern))
        
        pattern = '**/*.tmd' if recursive else '*.tmd'
        tmdl_files.extend(str(p) for p in path_obj.glob(pattern))
    
    return sorted(tmdl_files)


def validate_command(path: str, verbose: bool = False) -> int:
    """Validate TMDL files"""
    files = find_tmdl_files(path)
    
    if not files:
        print(f"No TMDL files found in: {path}")
        return 1
    
    print(f"Validating {len(files)} TMDL file(s)...\n")
    
    parser = TmdlParser()
    validator = TmdlValidator()
    
    total_errors = 0
    total_warnings = 0
    
    for file_path in files:
        tmdl_file = parser.parse_file(file_path)
        errors, warnings = validator.validate(tmdl_file)
        
        # Add parse errors
        errors.extend(tmdl_file.errors)
        warnings.extend(tmdl_file.warnings)
        
        total_errors += len(errors)
        total_warnings += len(warnings)
        
        if errors or warnings or verbose:
            rel_path = os.path.relpath(file_path)
            
            if errors:
                print(f"❌ {rel_path}: {len(errors)} error(s)")
                for err in errors:
                    print(f"   Line {err.line_number}: {err.message}")
            elif warnings:
                print(f"⚠️  {rel_path}: {len(warnings)} warning(s)")
                for warn in warnings:
                    print(f"   Line {warn.line_number}: {warn.message}")
            else:
                print(f"✅ {rel_path}: OK")
    
    print(f"\n{'='*50}")
    print(f"Total: {total_errors} error(s), {total_warnings} warning(s)")
    
    return 0 if total_errors == 0 else 1


def format_command(path: str, in_place: bool = True, check_only: bool = False) -> int:
    """Format TMDL files"""
    files = find_tmdl_files(path)
    
    if not files:
        print(f"No TMDL files found in: {path}")
        return 1
    
    print(f"{'Checking' if check_only else 'Formatting'} {len(files)} TMDL file(s)...\n")
    
    parser = TmdlParser()
    formatter = TmdlFormatter(use_tabs=True)
    
    files_changed = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ Cannot read {file_path}: {e}")
            continue
        
        # Convert spaces to tabs
        formatted_content = formatter.convert_spaces_to_tabs(original_content)
        
        # Check if content changed
        if original_content != formatted_content:
            files_changed += 1
            rel_path = os.path.relpath(file_path)
            
            if check_only:
                print(f"⚠️  {rel_path}: Would be reformatted")
            elif in_place:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                print(f"✅ {rel_path}: Reformatted")
            else:
                print(f"ℹ️  {rel_path}: Needs formatting")
        else:
            if not check_only:
                rel_path = os.path.relpath(file_path)
                print(f"✓  {rel_path}: No changes needed")
    
    print(f"\n{'='*50}")
    print(f"{'Would reformat' if check_only else 'Reformatted'}: {files_changed} file(s)")
    
    return 0 if (check_only and files_changed == 0) or not check_only else 1


def check_command(path: str) -> int:
    """Check TMDL files without modifying"""
    return format_command(path, in_place=False, check_only=True)


def main():
    parser = argparse.ArgumentParser(
        description='TMDL (Tabular Model Definition Language) Formatter and Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validate ./BMD_sales.SemanticModel/definition/
  %(prog)s format ./BMD_sales.SemanticModel/definition/tables/
  %(prog)s check ./BMD_sales.SemanticModel/

TMDL Specification:
  - Uses TAB characters for indentation (not spaces)
  - Object declarations: object_type object_name
  - Properties use colon: propertyName: value
  - Expressions use equals: measure Name = DAX_EXPRESSION
  - Multi-line blocks can use triple backticks (```)
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate TMDL file syntax')
    validate_parser.add_argument('path', help='Path to TMDL file or directory')
    validate_parser.add_argument('-v', '--verbose', action='store_true', help='Show all files, not just errors')
    
    # Format command
    format_parser = subparsers.add_parser('format', help='Format TMDL files (converts spaces to tabs)')
    format_parser.add_argument('path', help='Path to TMDL file or directory')
    format_parser.add_argument('--no-write', action='store_true', help="Don't write changes, just show what would change")
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if TMDL files need formatting')
    check_parser.add_argument('path', help='Path to TMDL file or directory')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        return validate_command(args.path, verbose=args.verbose)
    elif args.command == 'format':
        return format_command(args.path, in_place=not args.no_write)
    elif args.command == 'check':
        return check_command(args.path)
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
