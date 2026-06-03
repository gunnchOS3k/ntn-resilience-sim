#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from ntn_resilience.tool_adapters import ns3_export, sionna_link_export, standards_watch
ns3_export.export()
sionna_link_export.export()
standards_watch.export()
