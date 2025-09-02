#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from dbanalyzer.crew import DBAnalyzer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'requirement': 'For the last 12 months, find the top 5 departments at risk due to a mix of high attrition and pay compression.',
    }
    
    try:
        result = DBAnalyzer().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
