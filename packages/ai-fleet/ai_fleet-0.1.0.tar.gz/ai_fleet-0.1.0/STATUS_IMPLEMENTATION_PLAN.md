# AI Fleet Status Tracking Implementation Plan

## Overview
This document outlines the plan to enhance AI Fleet's `fleet list` command with real-time agent status tracking and watch mode functionality, inspired by the UZI project's implementation.

## Research Summary

### UZI's Approach
1. **Status Detection**: Captures tmux pane content and searches for specific strings
   - "esc to interrupt" or "Thinking" → status: "running"
   - Otherwise → status: "ready"
   - Capture failure → status: "unknown"

2. **Implementation Details**:
   - Uses `tmux capture-pane` command directly
   - Implements watch mode with 1-second refresh using ticker
   - Color-codes statuses (green for ready, yellow for running)
   - Displays git diff stats alongside status

### AI Fleet Current State
1. Only tracks "active" vs "dead" (based on tmux session existence)
2. Uses libtmux library for tmux interactions
3. No real-time status detection
4. No watch mode functionality

## Implementation Plan

### Phase 1: Add Status Detection

#### 1.1 Extend TmuxManager (tmux.py)
Add method to capture pane content for status detection:

```python
def get_pane_content(self, branch: str) -> Optional[str]:
    """Capture current pane content for status detection."""
    session_name = self._session_name(branch)
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session_name, "-p"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None
```

#### 1.2 Create Status Detection Logic
Add new method in TmuxManager or create a separate StatusDetector class:

```python
def get_agent_status(self, branch: str) -> str:
    """Detect current agent status from pane content."""
    content = self.get_pane_content(branch)
    if content is None:
        return "unknown"
    
    # Check for Claude-specific patterns
    if any(pattern in content for pattern in [
        "esc to interrupt",
        "Thinking",
        "I'll help",  # Claude response starting
        "Let me"      # Common Claude response pattern
    ]):
        return "running"
    
    # Check if waiting for input
    if content.strip().endswith(("$", ">", ":", "?")) or "Human:" in content:
        return "ready"
    
    return "idle"
```

#### 1.3 Update Agent Status Display
Modify list.py to:
- Use the new status detection
- Add color coding for different statuses
- Replace simple "active/dead" with detailed statuses

Status types:
- `ready` (green) - Waiting for prompt
- `running` (yellow) - Processing/thinking
- `idle` (blue) - No recent activity
- `dead` (red) - Session doesn't exist
- `unknown` (gray) - Can't determine status

### Phase 2: Add Watch Mode

#### 2.1 Add Watch Flag
Update list command in list.py:
```python
@click.option("--watch", "-w", is_flag=True, help="Watch mode - refresh every second")
```

#### 2.2 Implement Watch Loop
Add watch mode logic similar to UZI:

```python
def run_watch_mode(config, state, tmux_mgr, grouped, all):
    """Run list command in watch mode."""
    import time
    import sys
    
    try:
        while True:
            # Clear screen
            print("\033[H\033[2J", end="")
            
            # Run normal list logic
            display_agents(config, state, tmux_mgr, grouped, all)
            
            # Add timestamp
            print(f"\nLast updated: {datetime.now().strftime('%H:%M:%S')}")
            print("Press Ctrl+C to exit watch mode")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting watch mode")
        sys.exit(0)
```

### Phase 3: Additional Enhancements

#### 3.1 Add Model Information
- Extract model info from pane content or command history
- Store in state.json
- Display in list output

#### 3.2 Add Git Diff Stats
- Show additions/deletions like UZI does
- Use git commands to calculate diff stats per worktree

#### 3.3 Performance Optimization
- Cache pane content for multiple status checks
- Batch tmux capture commands if possible
- Consider using asyncio for concurrent status checks

## Implementation Steps

1. **Create feature branch**
   ```bash
   git checkout -b add-status-tracking
   ```

2. **Implement status detection**
   - Add `get_pane_content()` to TmuxManager
   - Add `get_agent_status()` method
   - Update list command to use new statuses

3. **Add watch mode**
   - Add --watch/-w flag
   - Implement watch loop with screen clearing
   - Handle keyboard interrupt gracefully

4. **Test thoroughly**
   - Test with various Claude states
   - Test watch mode refresh
   - Test with multiple agents
   - Test error conditions

5. **Update documentation**
   - Update README with new features
   - Add examples of watch mode
   - Document status types

## Testing Plan

### Unit Tests
- Test status detection with mock pane content
- Test watch mode timer
- Test status color formatting

### Integration Tests
- Test with real tmux sessions
- Test status transitions
- Test watch mode with multiple agents

### Manual Testing Checklist
- [ ] Status shows "ready" when Claude is waiting
- [ ] Status shows "running" when Claude is thinking
- [ ] Watch mode refreshes every second
- [ ] Ctrl+C exits watch mode cleanly
- [ ] Colors display correctly
- [ ] Performance is acceptable with 10+ agents

## Future Enhancements
1. Add status history/transitions
2. Add notifications when agents complete tasks
3. Add filtering by status
4. Add JSON output format for scripting
5. Consider WebSocket server for real-time updates