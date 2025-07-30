"""
Language detection patterns and mappings for the Language Detector Agent.
"""

# Map file extensions to languages
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "react",
    ".tsx": "react",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".php": "php",
    ".java": "java",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "c++",
    ".h": "c/c++ header",
    ".cs": "c#",
    ".swift": "swift",
    ".kt": "kotlin",
    ".sh": "shell",
    ".bat": "batch",
    ".ps1": "powershell",
    ".sql": "sql",
    ".md": "markdown",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".conf": "config",
    ".dart": "dart",
    ".lua": "lua",
    ".r": "r",
    ".scala": "scala",
    ".pl": "perl",
    ".ex": "elixir",
    ".exs": "elixir",
    ".elm": "elm",
    ".clj": "clojure",
    ".fs": "f#",
    ".hs": "haskell",
    ".vue": "vue",
    ".svelte": "svelte",
}

# Language detection patterns with weights
# Each pattern is a tuple of (regex_pattern, weight)
LANGUAGE_PATTERNS = {
    "python": [
        (r"import\s+[a-zA-Z0-9_]+", 0.3),
        (r"from\s+[a-zA-Z0-9_\.]+\s+import", 0.3),
        (r"def\s+[a-zA-Z0-9_]+\s*\(", 0.2),
        (r"class\s+[a-zA-Z0-9_]+\s*(\(|:)", 0.2),
        (r"if\s+__name__\s*==\s*['\"]__main__['\"]", 0.5),
        (r"@[a-zA-Z0-9_\.]+", 0.2),  # Decorators
    ],
    "javascript": [
        (r"const\s+[a-zA-Z0-9_]+\s*=", 0.3),
        (r"let\s+[a-zA-Z0-9_]+\s*=", 0.3),
        (r"var\s+[a-zA-Z0-9_]+\s*=", 0.2),
        (r"function\s+[a-zA-Z0-9_]+\s*\(", 0.3),
        (r"import\s+[a-zA-Z0-9_]+\s+from", 0.3),
        (r"export\s+(default\s+)?", 0.3),
        (r"document\.getElementById", 0.4),
        (r"window\.", 0.3),
    ],
    "typescript": [
        (r"interface\s+[a-zA-Z0-9_]+", 0.4),
        (r"type\s+[a-zA-Z0-9_]+\s*=", 0.4),
        (r":\s*[a-zA-Z0-9_]+", 0.2),  # Type annotations
        (r"<[a-zA-Z0-9_]+>", 0.3),  # Generic types
        (r"implements\s+", 0.4),
        (r"readonly\s+", 0.4),
    ],
    "java": [
        (r"public\s+class", 0.4),
        (r"private|protected|public", 0.2),
        (r"import\s+java\.", 0.5),
        (r"extends\s+[A-Z][a-zA-Z0-9_]+", 0.3),
        (r"implements\s+[A-Z][a-zA-Z0-9_]+", 0.3),
    ],
    "php": [
        (r"<\?php", 0.8),
        (r"\$[a-zA-Z0-9_]+", 0.3),
        (r"function\s+[a-zA-Z0-9_]+\s*\(", 0.3),
        (r"namespace\s+[a-zA-Z0-9_\\]+", 0.4),
        (r"use\s+[a-zA-Z0-9_\\]+", 0.3),
    ],
    "ruby": [
        (r"require\s+['\"][a-zA-Z0-9_/]+['\"]", 0.4),
        (r"def\s+[a-zA-Z0-9_]+", 0.3),
        (r"class\s+[A-Z][a-zA-Z0-9_]*", 0.3),
        (r"module\s+[A-Z][a-zA-Z0-9_]*", 0.3),
        (r"attr_accessor", 0.5),
    ],
    "go": [
        (r"package\s+[a-zA-Z0-9_]+", 0.5),
        (r"import\s+\(", 0.4),
        (r"func\s+[a-zA-Z0-9_]+", 0.3),
        (r"type\s+[a-zA-Z0-9_]+\s+struct", 0.4),
        (r"func\s+\([a-zA-Z0-9_]+\s+\*?[A-Z][a-zA-Z0-9_]*\)", 0.5),  # Methods
    ],
    "rust": [
        (r"fn\s+[a-zA-Z0-9_]+", 0.4),
        (r"let\s+mut", 0.5),
        (r"impl\s+[a-zA-Z0-9_]+", 0.4),
        (r"use\s+[a-zA-Z0-9_:]+", 0.3),
        (r"pub\s+struct", 0.4),
    ],
    "c": [
        (r"#include\s+<[a-zA-Z0-9_\.]+>", 0.5),
        (r"int\s+main\s*\(", 0.5),
        (r"void\s+[a-zA-Z0-9_]+\s*\(", 0.3),
        (r"struct\s+[a-zA-Z0-9_]+\s*\{", 0.3),
        (r"typedef", 0.4),
    ],
    "c++": [
        (r"#include\s+<[a-zA-Z0-9_\.]+>", 0.3),
        (r"class\s+[a-zA-Z0-9_]+", 0.4),
        (r"::\s*[a-zA-Z0-9_]+", 0.4),
        (r"std::", 0.5),
        (r"template\s*<", 0.5),
    ],
}

# Version-specific language features
LANGUAGE_VERSION_FEATURES = {
    "python": {
        "3.10+": ["match case", "pattern matching"],
        "3.9+": ["dictionary union operator |"],
        "3.8+": ["walrus operator :=", "f-string ="],
        "3.7+": ["dataclasses", "breakpoint()"],
        "3.6+": ["f-strings", "async generators", "variable annotations"],
        "3.5+": ["async/await", "type hints"],
        "3.0+": ["print()", "exception as"],
    },
    "javascript": {
        "ES2022+": ["at()", "class fields", "top level await"],
        "ES2021+": ["replaceAll", "numeric separators", "logical assignment"],
        "ES2020+": ["optional chaining", "nullish coalescing", "BigInt"],
        "ES2019+": ["flat", "flatMap", "trimStart", "trimEnd"],
        "ES2018+": ["rest/spread properties", "async iteration", "Promise.finally"],
        "ES2017+": ["async/await", "Object.values", "Object.entries"],
        "ES2015+": ["let/const", "arrow functions", "classes", "template literals", "destructuring"],
    },
    "java": {
        "17+": ["sealed classes", "pattern matching for switch"],
        "16+": ["records", "instanceof pattern matching"],
        "14+": ["switch expressions"],
        "11+": ["var keyword", "HTTP client"],
        "10+": ["local variable type inference"],
        "9+": ["modules", "private interface methods"],
        "8+": ["lambda expressions", "streams", "default methods"],
    },
}

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "python": {
        "django": ["django", "urls.py", "settings.py", "INSTALLED_APPS"],
        "flask": ["flask", "Flask(__name__)", "@app.route"],
        "fastapi": ["fastapi", "APIRouter", "@app.get"],
        "pytorch": ["torch", "nn.Module", "torch.tensor"],
        "tensorflow": ["tensorflow", "tf.", "keras"],
        "pandas": ["pandas", "pd.", "DataFrame"],
        "numpy": ["numpy", "np.", "ndarray"],
    },
    "javascript": {
        "react": ["React", "useState", "useEffect", "ReactDOM"],
        "vue": ["Vue", "createApp", "v-if", "v-for"],
        "angular": ["@Component", "ngOnInit", "NgModule"],
        "express": ["express", "app.get", "app.use", "req, res"],
        "next.js": ["next", "getStaticProps", "getServerSideProps"],
        "jquery": ["$", "jQuery", ".ready("],
    },
    "java": {
        "spring": ["@Controller", "@Service", "@Repository", "@Autowired"],
        "hibernate": ["@Entity", "@Table", "SessionFactory"],
        "junit": ["@Test", "Assert.", "assertEquals"],
        "android": ["Activity", "Fragment", "findViewById"],
    },
}
