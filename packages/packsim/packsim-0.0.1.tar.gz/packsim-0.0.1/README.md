# Description
A set of bin packing visualization simulation environment code, which can visualize the entire bin packing process, making it convenient for others to train or test

# How to use?
from packsim import simulate

# Default use
simulate()

# Customize use
simulate({ 'setting': 1, 'data': 'occupancy', 'test_data_config': 0, 'gui': 1, 'config': '/home/wzf/Workspace/rl/pypi/ttt/default.yaml', 'action_path': '/home/wzf/Workspace/rl/pypi/ttt/action.json', 'planning_time_path': '/home/wzf/Workspace/rl/pypi/ttt/planning_time.json', 'save_path': '/home/wzf/Workspace/rl/pypi/ttt'})

