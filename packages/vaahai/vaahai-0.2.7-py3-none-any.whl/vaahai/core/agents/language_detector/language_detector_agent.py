"""
Language Detector Agent

Agent specialized in detecting programming languages, features, and versions from code.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import autogen
from vaahai.core.agents.base import VaahaiAgent
from vaahai.core.agents.language_detector.prompts import (
    LANGUAGE_DETECTOR_SYSTEM_PROMPT,
    LANGUAGE_DETECTION_PROMPT_TEMPLATE,
    MULTI_FILE_ANALYSIS_PROMPT_TEMPLATE,
)
from vaahai.core.agents.language_detector.language_patterns import (
    EXTENSION_MAP,
    LANGUAGE_PATTERNS,
    LANGUAGE_VERSION_FEATURES,
    FRAMEWORK_PATTERNS,
)


class LanguageDetectorAgent(VaahaiAgent):
    """
    Agent specialized in detecting programming languages, features, and versions from code.
    
    This agent uses a combination of heuristic pattern matching and LLM-based analysis
    to identify programming languages, estimate versions based on syntax features,
    and detect frameworks and libraries being used.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Language Detector Agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(config)
        
        # Get Autogen config
        llm_config = self._create_autogen_config()
        
        # Initialize Autogen assistant agent
        self.autogen_agent = autogen.AssistantAgent(
            name="language_detector_agent",
            llm_config=llm_config,
            system_message=LANGUAGE_DETECTOR_SYSTEM_PROMPT
        )
        
        # Initialize user proxy for interaction
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )
        
        # Initialize language detection state
        self.detected_languages = {}
        self.file_languages = {}
        self.language_distribution = {}
    
    def detect_from_extension(self, file_path: str) -> str:
        """
        Detect language based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language name or "unknown"
        """
        ext = Path(file_path).suffix.lower()
        return EXTENSION_MAP.get(ext, "unknown")
    
    def detect_from_content(self, content: str) -> Dict[str, float]:
        """
        Detect programming language from file content using pattern matching.
        
        Args:
            content: File content to analyze
            
        Returns:
            Dictionary mapping language names to confidence scores
        """
        language_scores = {}
        
        # Check for shebang in scripts
        shebang_match = re.match(r'^#!.*?([a-zA-Z0-9]+)$', content.strip())
        if shebang_match:
            interpreter = shebang_match.group(1).lower()
            if interpreter in ['python', 'python3', 'python2']:
                language_scores['python'] = 0.9
            elif interpreter in ['node', 'nodejs']:
                language_scores['javascript'] = 0.9
            elif interpreter in ['ruby']:
                language_scores['ruby'] = 0.9
            # Add more interpreter mappings as needed
        
        # Check for language patterns
        for language, patterns in LANGUAGE_PATTERNS.items():
            score = 0
            for pattern, weight in patterns:
                if re.search(pattern, content):
                    score += weight
            
            if score > 0:
                language_scores[language] = score
        
        # Normalize scores
        total_score = sum(language_scores.values())
        if total_score > 0:
            for lang in language_scores:
                language_scores[lang] = language_scores[lang] / total_score
                
        return language_scores
    
    def detect_features(self, language: str, content: str) -> List[str]:
        """
        Detect language-specific features used in the code.
        
        Args:
            language: Detected programming language
            content: File content to analyze
            
        Returns:
            List of detected features
        """
        features = []
        
        # Check for language-specific features
        if language in LANGUAGE_VERSION_FEATURES:
            for version, version_features in LANGUAGE_VERSION_FEATURES[language].items():
                for feature in version_features:
                    # Simple check for feature keywords
                    # In a real implementation, this would use more sophisticated pattern matching
                    if feature in content:
                        features.append(feature)
        
        return features
    
    def detect_frameworks(self, language: str, content: str) -> List[Dict[str, Any]]:
        """
        Detect frameworks and libraries used in the code.
        
        Args:
            language: Detected programming language
            content: File content to analyze
            
        Returns:
            List of detected frameworks with confidence scores
        """
        frameworks = []
        
        # Check for framework-specific patterns
        if language in FRAMEWORK_PATTERNS:
            for framework, patterns in FRAMEWORK_PATTERNS[language].items():
                evidence = []
                for pattern in patterns:
                    if pattern in content:
                        evidence.append(pattern)
                
                if evidence:
                    confidence = min(0.3 + (len(evidence) / len(patterns)) * 0.7, 1.0)
                    frameworks.append({
                        "name": framework,
                        "confidence": confidence,
                        "evidence": evidence
                    })
        
        return frameworks
    
    def estimate_version(self, language: str, content: str) -> Dict[str, Any]:
        """
        Estimate the language version based on features used.
        
        Args:
            language: Detected programming language
            content: File content to analyze
            
        Returns:
            Dictionary with version information
        """
        if language not in LANGUAGE_VERSION_FEATURES:
            return {
                "detected": "unknown",
                "confidence": 0,
                "features": []
            }
        
        # Check for version-specific features
        version_features = {}
        for version, features in LANGUAGE_VERSION_FEATURES[language].items():
            version_features[version] = []
            for feature in features:
                # Simple check for feature keywords
                # In a real implementation, this would use more sophisticated pattern matching
                if feature in content:
                    version_features[version].append(feature)
        
        # Find the highest version with detected features
        detected_version = "unknown"
        detected_features = []
        for version, features in version_features.items():
            if features and (detected_version == "unknown" or version > detected_version):
                detected_version = version
                detected_features = features
        
        # Calculate confidence based on number of features detected
        confidence = 0
        if detected_features:
            # Simple confidence calculation
            # In a real implementation, this would be more sophisticated
            confidence = min(0.5 + (len(detected_features) * 0.1), 0.9)
        
        return {
            "detected": detected_version,
            "confidence": confidence,
            "features": detected_features
        }
    
    async def analyze_with_llm(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Analyze code using the LLM for more sophisticated detection.
        
        Args:
            file_path: Path to the file
            content: File content to analyze
            
        Returns:
            Dictionary with LLM analysis results
        """
        # Prepare prompt with code and file path
        prompt = LANGUAGE_DETECTION_PROMPT_TEMPLATE.format(
            code=content,
            file_path=file_path
        )
        
        # Initialize chat between user proxy and assistant
        self.user_proxy.initiate_chat(
            self.autogen_agent,
            message=prompt
        )
        
        # Get the last message from the assistant
        response = self.user_proxy.chat_messages[self.autogen_agent.name][-1]["content"]
        
        # Extract JSON from the response
        try:
            # Find JSON block in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code block markers
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    return {"error": "Could not extract JSON from LLM response"}
            
            # Parse JSON
            analysis = json.loads(json_str)
            return analysis
        except (json.JSONDecodeError, AttributeError) as e:
            return {"error": f"Error parsing LLM response: {str(e)}"}
    
    def detect_language(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Detect programming language, version, and features from a file using heuristic methods.
        
        Args:
            file_path: Path to the file
            content: File content to analyze
            
        Returns:
            Dictionary with language detection results
        """
        # Initial detection from extension
        ext_language = self.detect_from_extension(file_path)
        
        # Content-based detection
        language_scores = self.detect_from_content(content)
        
        # Determine primary language
        primary_language = ext_language
        confidence = 0.5  # Default confidence
        
        if language_scores:
            # If content detection found languages, use the highest scoring one
            primary_language, confidence = max(language_scores.items(), key=lambda x: x[1])
        
        # If extension-based detection disagrees with content-based detection,
        # adjust confidence based on the strength of the content-based detection
        if ext_language != "unknown" and ext_language != primary_language:
            if confidence > 0.7:
                # Content detection is strong, keep it
                pass
            else:
                # Extension detection is more reliable for weak content detection
                primary_language = ext_language
                confidence = 0.6
        
        # Store results for this file
        self.file_languages[file_path] = primary_language
        
        # Update language distribution
        if primary_language in self.language_distribution:
            self.language_distribution[primary_language] += 1
        else:
            self.language_distribution[primary_language] = 1
        
        # Detect features
        features = self.detect_features(primary_language, content)
        
        # Detect frameworks
        frameworks = self.detect_frameworks(primary_language, content)
        
        # Estimate version
        version_info = self.estimate_version(primary_language, content)
        
        # Prepare heuristic analysis
        analysis = {
            "language": primary_language,
            "confidence": confidence,
            "version": version_info,
            "frameworks": frameworks,
            "features": features,
            "additional_languages": [],
            "analysis": f"Detected {primary_language} based on file extension and content patterns."
        }
        
        return analysis
    
    async def run(self, file_paths: List[str], file_contents: List[str], use_llm: bool = True) -> Dict[str, Any]:
        """
        Run language detection on the provided files.
        
        Args:
            file_paths: List of file paths to analyze
            file_contents: List of file contents corresponding to file_paths
            use_llm: Whether to use LLM for enhanced detection
            
        Returns:
            Dictionary with language detection results
        """
        # Reset state for new analysis
        self.file_languages = {}
        self.language_distribution = {}
        
        # Process each file
        file_analyses = {}
        for path, content in zip(file_paths, file_contents):
            # First use heuristic detection
            heuristic_analysis = self.detect_language(path, content)
            
            # If LLM is enabled and we have a valid API key, enhance with LLM analysis
            if use_llm and not self._create_autogen_config().get("use_dummy_config", False):
                try:
                    llm_analysis = await self.analyze_with_llm(path, content)
                    
                    # Combine heuristic and LLM analyses
                    if "error" not in llm_analysis:
                        # LLM analysis takes precedence for most fields
                        combined_analysis = {
                            "language": llm_analysis.get("language", heuristic_analysis["language"]),
                            "confidence": llm_analysis.get("confidence", heuristic_analysis["confidence"]),
                            "version": llm_analysis.get("version", heuristic_analysis["version"]),
                            "frameworks": llm_analysis.get("frameworks", heuristic_analysis["frameworks"]),
                            "features": list(set(
                                heuristic_analysis["features"] + 
                                llm_analysis.get("version", {}).get("features", [])
                            )),
                            "additional_languages": llm_analysis.get("additional_languages", []),
                            "analysis": llm_analysis.get("analysis", heuristic_analysis["analysis"])
                        }
                        file_analyses[path] = combined_analysis
                    else:
                        # Fall back to heuristic analysis if LLM analysis failed
                        file_analyses[path] = heuristic_analysis
                except Exception as e:
                    # Fall back to heuristic analysis on error
                    file_analyses[path] = heuristic_analysis
                    file_analyses[path]["error"] = f"LLM analysis failed: {str(e)}"
            else:
                # Use only heuristic analysis
                file_analyses[path] = heuristic_analysis
        
        # Determine primary project language
        primary_language = None
        if self.language_distribution:
            primary_language = max(self.language_distribution.items(), key=lambda x: x[1])[0]
        
        # Create project-level summary
        summary = {
            "primary_language": primary_language,
            "language_distribution": self.language_distribution,
            "file_count": len(file_paths),
            "file_analyses": file_analyses
        }
        
        return summary
