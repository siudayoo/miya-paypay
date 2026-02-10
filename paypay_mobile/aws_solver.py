"""
PayPay Mobile - AWS WAF Captcha Solver

This module handles AWS WAF CAPTCHA challenges that may appear during login.
Based on paypaypy's AWS Solver implementation.
"""
import re
import time
import json
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from .exceptions import AuthenticationException, NetworkException


class AWSCaptchaSolver:
    """Solver for AWS WAF CAPTCHA challenges"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        
    def solve_captcha(self, response: requests.Response) -> Optional[str]:
        """
        Solve AWS WAF CAPTCHA if present in response
        
        Args:
            response: Response that may contain CAPTCHA challenge
            
        Returns:
            Cookie value if CAPTCHA was solved, None if no CAPTCHA present
            
        Raises:
            AuthenticationException: If CAPTCHA solving fails
        """
        # Check if response contains AWS WAF CAPTCHA
        if not self._has_captcha(response):
            return None
            
        try:
            # Extract CAPTCHA parameters from response
            captcha_params = self._extract_captcha_params(response)
            if not captcha_params:
                raise AuthenticationException("Failed to extract CAPTCHA parameters")
            
            # Solve the CAPTCHA challenge
            cookie_value = self._solve_challenge(captcha_params)
            
            return cookie_value
            
        except Exception as e:
            raise AuthenticationException(f"CAPTCHA solving failed: {str(e)}")
    
    def _has_captcha(self, response: requests.Response) -> bool:
        """Check if response contains AWS WAF CAPTCHA"""
        content = response.text
        return (
            'aws-waf-token' in content or
            'AwsWafCaptcha' in content or
            'challenge.aws' in content
        )
    
    def _extract_captcha_params(self, response: requests.Response) -> Optional[Dict[str, str]]:
        """Extract CAPTCHA parameters from response HTML"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the script containing CAPTCHA parameters
            script_pattern = re.compile(r'AwsWafCaptcha\.renderCaptcha\((.*?)\);', re.DOTALL)
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string:
                    match = script_pattern.search(script.string)
                    if match:
                        # Extract JSON parameters
                        params_str = match.group(1)
                        # Clean up the parameters string
                        params_str = re.sub(r'(\w+):', r'"\1":', params_str)
                        params = json.loads(params_str)
                        return params
            
            # Alternative extraction method
            api_url_match = re.search(r'apiUrl:\s*["\']([^"\']+)["\']', response.text)
            container_match = re.search(r'container:\s*["\']([^"\']+)["\']', response.text)
            
            if api_url_match and container_match:
                return {
                    'apiUrl': api_url_match.group(1),
                    'container': container_match.group(1)
                }
                
        except Exception as e:
            print(f"Error extracting CAPTCHA params: {e}")
        
        return None
    
    def _solve_challenge(self, captcha_params: Dict[str, str]) -> str:
        """
        Solve the CAPTCHA challenge using AWS WAF API
        
        Args:
            captcha_params: CAPTCHA parameters extracted from HTML
            
        Returns:
            AWS WAF token cookie value
        """
        api_url = captcha_params.get('apiUrl', '')
        
        if not api_url:
            raise AuthenticationException("Missing API URL for CAPTCHA")
        
        # Prepare CAPTCHA solve request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # AWS WAF CAPTCHA solving typically involves:
        # 1. Fetching the challenge
        # 2. Computing the solution
        # 3. Submitting the solution
        
        try:
            # Fetch challenge
            challenge_response = self.session.get(api_url, headers=headers)
            challenge_data = challenge_response.json()
            
            # Simulate solving (in real implementation, this would solve the actual puzzle)
            # For demonstration, we'll use a delay to simulate solving time
            time.sleep(2)
            
            # Submit solution
            solution_data = {
                'token': challenge_data.get('token'),
                'solution': self._compute_solution(challenge_data)
            }
            
            solution_response = self.session.post(
                api_url,
                json=solution_data,
                headers=headers
            )
            
            result = solution_response.json()
            
            # Extract the WAF token from response
            waf_token = result.get('token') or result.get('cookie')
            
            if waf_token:
                return waf_token
            
            raise AuthenticationException("No token received from CAPTCHA solution")
            
        except requests.RequestException as e:
            raise NetworkException(f"Network error during CAPTCHA solving: {str(e)}")
    
    def _compute_solution(self, challenge_data: Dict[str, Any]) -> str:
        """
        Compute the solution to the CAPTCHA challenge
        
        Note: This is a placeholder. Actual implementation would depend on
        the specific CAPTCHA type (puzzle, image recognition, etc.)
        
        Args:
            challenge_data: Challenge data from AWS WAF
            
        Returns:
            Solution string
        """
        # This would contain the actual solving logic
        # For now, return a placeholder
        return challenge_data.get('token', '')
    
    def apply_token_to_session(self, token: str, domain: str = '.paypay.ne.jp'):
        """
        Apply the solved CAPTCHA token to the session cookies
        
        Args:
            token: AWS WAF token value
            domain: Cookie domain
        """
        cookie = requests.cookies.create_cookie(
            name='aws-waf-token',
            value=token,
            domain=domain,
            path='/',
            secure=True
        )
        self.session.cookies.set_cookie(cookie)


def handle_aws_captcha(session: requests.Session, response: requests.Response) -> bool:
    """
    Convenience function to handle AWS CAPTCHA if present
    
    Args:
        session: Requests session
        response: Response that may contain CAPTCHA
        
    Returns:
        True if CAPTCHA was present and solved, False if no CAPTCHA
    """
    solver = AWSCaptchaSolver(session)
    token = solver.solve_captcha(response)
    
    if token:
        solver.apply_token_to_session(token)
        return True
    
    return False
