# Script containing the logic that will be used to sniff the Java source files

import javalang

from typing import Union

from collections import namedtuple

# TODO. if these are the same than the ones in python, we should move them to a shared module
FunctionSpecs = namedtuple(
    "FunctionSpecs", ["name", "docstring", "start_lineno", "end_lineno"]
)


class JavaScriptSniffer:
    """
    This class will scrape all the code from a Java source file and return the list of functions (methods).

    Additionally, it will capture features of those functions such as the JavaDoc comment (docstring),
    start and end lines.

    This will be used later on to determine the amount of telemetry calls in a script.

    Args:
        filename [str]: the Java source file to be sniffed
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.functions_list = []

        with open(self.filename, "r") as f:
            self.source_code = f.read()
            self.lines = self.source_code.splitlines()

    def _get_javadoc_for_method(self, method_node, comments):
        """
        Check if the method provided has a JavaDoc comment immediately preceding it.

        Args:
            method_node: javalang.tree.MethodDeclaration node
            comments: list of (pos, comment_text) tuples

        Returns:
            str: JavaDoc comment without leading /** and trailing */, stripped; None if none found

        Example:
            Given the method preceded by the comment:
            ```
            /**
             * Example method JavaDoc
             */
            public void example() { ... }
            ```
            The returned string will be:
            ```
            "Example method JavaDoc"
            ```
        """

        method_line = method_node.position.line if method_node.position else None
        if method_line is None:
            return None

        preceding_comments = [c for c in comments if c[0] < method_line]
        if not preceding_comments:
            return None

        closest_comment_line, comment_text = max(preceding_comments, key=lambda c: c[0])

        if comment_text.strip().startswith("/**") and comment_text.strip().endswith(
            "*/"
        ):
            cleaned = comment_text.strip()[3:-2].strip()
            return cleaned

        return None

    def _estimate_method_end(self, start_line):
        """
        Estimate method end line by counting braces from start_line in the source file.

        Args:
            start_line [int]: starting line of method

        Returns:
            int: estimated end line number

        Example:
            For method starting at line 10, counts braces until balanced,
            returning e.g. line 15 if the closing brace is at line 15.
        """

        if start_line == -1:
            return -1

        brace_count = 0
        in_method = False
        for i, line in enumerate(self.lines[start_line - 1 :], start=start_line):
            brace_count += line.count("{")
            brace_count -= line.count("}")
            if brace_count > 0:
                in_method = True
            if in_method and brace_count == 0:
                return i

        return len(self.lines)

    def _extract_comments(self):
        """
        Extract JavaDoc comments and their line numbers from source code.

        Returns:
            list of (line_number, comment_text) tuples

        Example:
            Given source code with JavaDoc starting at line 2:
            ```
            /**
             * Sample JavaDoc comment
             */
            ```
            Will return:
            ```
            [(2, "/**\n * Sample JavaDoc comment\n */")]
            ```
        """

        comments = []
        in_javadoc = False
        javadoc_lines = []
        javadoc_start_line = None

        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()

            if stripped.startswith("/**"):
                in_javadoc = True
                javadoc_lines = [line]
                javadoc_start_line = idx
                continue

            if in_javadoc:
                javadoc_lines.append(line)
                if "*/" in line:
                    in_javadoc = False
                    comment_text = "\n".join(javadoc_lines)
                    comments.append((javadoc_start_line, comment_text))
                    javadoc_lines = []
                    javadoc_start_line = None

        return comments

    def visit_methods(self, tree, comments):
        """
        Visit method declarations in the AST and capture features.

        Args:
            tree: parsed javalang tree
            comments: list of (line_number, comment_text)

        Example:
            After parsing, this method will populate `self.functions_list` with
            NamedTuples for each method, e.g.
            ```
            FunctionSpecs(name='myMethod', docstring='This is a sample Java method.', start_lineno=2, end_lineno=5)
            ```
        """
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            start_line = node.position.line if node.position else -1

            end_line = self._estimate_method_end(start_line)
            docstring = self._get_javadoc_for_method(node, comments)

            func_spec = FunctionSpecs(
                name=node.name,
                docstring=docstring,
                start_lineno=start_line,
                end_lineno=end_line,
            )

            self.functions_list.append(func_spec)

    def run(self):
        """
        Run the sniffer over the Java source file.

        This will parse the source file and then visit all method declarations to capture their specs.

        Example:
            ```
            sniffer = JavaScriptSniffer('Example.java')
            sniffer.run()
            print(sniffer.functions_list)
            ```
        """
        tree = javalang.parse.parse(self.source_code)
        comments = self._extract_comments()
        self.visit_methods(tree, comments)
