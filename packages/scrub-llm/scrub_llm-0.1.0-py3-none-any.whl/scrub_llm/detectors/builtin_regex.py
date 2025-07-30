import re
from typing import List, Dict, Pattern
from .base import Detector, Match


class RegexDetector(Detector):
    def __init__(self):
        self.patterns: Dict[str, Pattern[str]] = self._compile_patterns()
    
    @property
    def name(self) -> str:
        return "regex_detector"
    
    def _compile_patterns(self) -> Dict[str, Pattern[str]]:
        patterns = {
            "aws_access_key_id": r"AKIA[0-9A-Z]{16}",
            "aws_secret_key": r"[0-9a-zA-Z/+=]{40}",
            "github_token": r"gh[ps]_[0-9a-zA-Z]{36}",
            "gitlab_token": r"glpat-[0-9a-zA-Z\-\_]{20}",
            "slack_token": r"xox[baprs]-[0-9a-zA-Z\-]{10,}",
            "slack_webhook": r"https://hooks\.slack\.com/services/T[0-9A-Z]{8,}/B[0-9A-Z]{8,}/[0-9a-zA-Z]{24}",
            "stripe_key": r"(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}",
            "jwt_token": r"ey[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_.+/=]*",
            "gcp_api_key": r"AIza[0-9A-Za-z\-_]{35}",
            "gcp_oauth": r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
            "azure_key": r"[0-9a-zA-Z]{32}",
            "mailgun_key": r"key-[0-9a-zA-Z]{32}",
            "twilio_key": r"SK[0-9a-fA-F]{32}",
            "npm_token": r"npm_[0-9a-zA-Z]{36}",
            "sendgrid_key": r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}",
            "datadog_key": r"[a-z0-9]{32}",
            "datadog_app_key": r"[a-z0-9]{40}",
            "openai_api_key": r"sk-[0-9a-zA-Z]{48}",
            "anthropic_api_key": r"sk-ant-[0-9a-zA-Z]{90,}",
            "discord_token": r"[MN][0-9a-zA-Z]{23}\.[0-9a-zA-Z_-]{6}\.[0-9a-zA-Z_-]{27}",
            "discord_webhook": r"https://discord(app)?\.com/api/webhooks/[0-9]+/[0-9a-zA-Z_-]+",
            "heroku_api_key": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            "mailchimp_key": r"[0-9a-f]{32}-us[0-9]{1,2}",
            "private_key_header": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            "ssh_private_key": r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----[\\s\\S]+?-----END (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----",
            "pgp_private_key": r"-----BEGIN PGP PRIVATE KEY BLOCK-----[\\s\\S]+?-----END PGP PRIVATE KEY BLOCK-----",
            "generic_api_key": r"[aA][pP][iI]_?[kK][eE][yY]\\s*[:=]\\s*['\"][0-9a-zA-Z_\\-]{20,}['\"]",
            "generic_secret": r"[sS][eE][cC][rR][eE][tT]\\s*[:=]\\s*['\"][0-9a-zA-Z_\\-]{20,}['\"]",
            "password_in_url": r"(https?|ftp)://[^:]+:[^@]+@[^/]+",
        }
        
        return {name: re.compile(pattern) for name, pattern in patterns.items()}
    
    def scan(self, text: str) -> List[Match]:
        matches = []
        
        for pattern_name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                matches.append(Match(
                    pattern_name=pattern_name,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                ))
        
        return matches