# Seamstress Roadmap

## Current Status (v0.1.0)

Seamstress has been successfully unified from multiple development branches (V1-V4) into a cohesive productivity tool. The current build is functional and includes:

- ✅ Core focus tracking with keyboard and webcam monitoring
- ✅ Project/thread management via "barges" metaphor
- ✅ Time capsule recording with optional macOS context probes
- ✅ Calendar integration (ICS + Google OAuth)
- ✅ Daily and weekly visualizations
- ✅ Offline focus analysis from CSV
- ✅ Local LLM summarization (Ollama)
- ✅ Streamlit dashboard
- ✅ Robust state serialization

---

## Immediate Fixes Needed

### High Priority Bugs

#### 1. **WorkBlock Persistence**
**Issue:** `visualize` command shows no data because focus sessions don't persist work blocks properly  
**Impact:** Medium - visualization features unusable without data  
**Fix Required:**
- Verify `FocusMonitor._finalize_block()` is called on session end
- Test that interrupted sessions (Ctrl+C) still save blocks
- Add debug logging to track block saves

**Estimated Effort:** 2 hours

#### 2. **Timezone Edge Cases**
**Status:** Mostly fixed, but needs testing  
**Remaining work:**
- Test ICS files with mixed timezone formats
- Verify daily visualization handles DST transitions
- Add unit tests for timezone normalization

**Estimated Effort:** 3 hours

#### 3. **Task Display Formatting**
**Issue:** Dict-based tasks in YAML show as quoted dict strings in board view  
**Status:** Fixed with string flattening, but format could be cleaner  
**Enhancement:**
- Custom YAML schema validation
- Better task serialization for complex structures
- Visual indicators for multi-part tasks

**Estimated Effort:** 4 hours

---

## Short-Term Enhancements (1-2 weeks)

### 1. **Enhanced Focus Session UI**
- [ ] Add progress bar showing time remaining in session
- [ ] Show recent keystrokes/minute trend
- [ ] Display break countdown timer
- [ ] Add sound/notification for break prompts

**Value:** Improves real-time session experience  
**Effort:** 6 hours

### 2. **State Migration Tool**
- [ ] Script to convert old state formats to current schema
- [ ] Backup automation before state operations
- [ ] Version detection in state files
- [ ] Migration dry-run mode

**Value:** Prevents data loss during updates  
**Effort:** 4 hours

### 3. **Calendar Export**
- [ ] Export sprint plans as ICS files
- [ ] Import back into Google Calendar / Apple Calendar
- [ ] Two-way sync for completed blocks
- [ ] Conflict detection with existing events

**Value:** Closes the planning loop  
**Effort:** 8 hours

### 4. **Test Suite**
- [ ] Unit tests for data models
- [ ] Integration tests for CLI commands
- [ ] Fixture data for testing
- [ ] CI/CD setup (GitHub Actions)

**Value:** Prevents regressions  
**Effort:** 12 hours

---

## Medium-Term Features (1-2 months)

### 1. **Improved Visualizations**

#### Weekly Dashboard
- Heatmap view of focus hours by day/time
- Trend lines for focus scores
- Project velocity tracking
- Landfall deadline countdown

**Effort:** 8 hours

#### Gantt-Style Timeline
- Multi-project view showing parallel work
- Critical path highlighting for barges
- Resource allocation visualization

**Effort:** 10 hours

### 2. **Streamlit Dashboard Enhancements**
Current dashboard is basic. Enhance with:
- [ ] Real-time session monitoring
- [ ] Interactive plan editing
- [ ] Drag-and-drop schedule adjustments
- [ ] Focus session history browser
- [ ] Time capsule search and tagging

**Effort:** 16 hours

### 3. **macOS Menu Bar App**
- [ ] Quick session start/stop
- [ ] Current focus timer display
- [ ] Today's plan at a glance
- [ ] Notification integration

**Tech:** PyObjC or rumps  
**Effort:** 20 hours

### 4. **Advanced Focus Features**

#### Context Capture
- [ ] Automatic app/window tracking
- [ ] Git branch detection
- [ ] Open file lists from IDEs
- [ ] Browser tab snapshots

**Effort:** 12 hours

#### Adaptive Breaks
- [ ] Learn user's optimal break timing
- [ ] Adjust thresholds based on focus patterns
- [ ] Pomodoro mode option
- [ ] Integration with break apps (Stretchly, etc.)

**Effort:** 10 hours

### 5. **Enhanced Time Capsules**

#### Multimedia Support
- [ ] Screenshot attachments
- [ ] Audio memo recording
- [ ] Video clip capture
- [ ] Markdown rich-text notes

**Effort:** 12 hours

#### Search & Analytics
- [ ] Full-text search across capsules
- [ ] Tag taxonomy
- [ ] Topic clustering via embeddings
- [ ] Capsule-to-capsule relationships

**Effort:** 16 hours

---

## Long-Term Vision (3-6 months)

### 1. **Mobile Companion**
- iOS/Android app for:
  - Quick capsule recording
  - Plan viewing
  - Break reminders
  - Progress tracking
- Data sync via iCloud/Dropbox/self-hosted

**Effort:** 40+ hours

### 2. **Collaboration Features**
- [ ] Shared barges for team projects
- [ ] Capsule sharing with permissions
- [ ] Team focus statistics
- [ ] Meeting time suggestions based on focus patterns

**Tech:** Consider lightweight sync (Git-based?) or self-hosted server  
**Effort:** 60+ hours

### 3. **AI Enhancements**

#### Smart Scheduling
- [ ] ML-based optimal time slot prediction
- [ ] Auto-categorize unplanned work
- [ ] Suggest task breakdowns for threads
- [ ] Detect scope creep and alert

**Effort:** 30 hours

#### Natural Language Interface
- [ ] Voice commands for session start
- [ ] Text-based capsule creation
- [ ] Query interface ("What did I work on last Tuesday?")
- [ ] Weekly report generation

**Tech:** Ollama + RAG pipeline  
**Effort:** 25 hours

### 4. **Cross-Platform Support**
- [ ] Windows support (pynput works, test other features)
- [ ] Linux support (same)
- [ ] WSL-friendly operations
- [ ] Platform-specific context probes

**Effort:** 20 hours

### 5. **Integration Ecosystem**

#### Time Tracking
- [ ] Toggl export/import
- [ ] RescueTime integration
- [ ] Clockify sync

#### Project Management
- [ ] Notion database sync
- [ ] GitHub Issues → Threads
- [ ] Jira integration
- [ ] Obsidian daily notes

#### Calendars
- [ ] Microsoft Outlook
- [ ] Apple Calendar direct integration
- [ ] CalDAV support

**Effort:** 40+ hours total

---

## Technical Debt

### Code Quality
- [ ] Type hints throughout (currently mixed)
- [ ] Docstring coverage (many modules missing)
- [ ] Consistent error handling
- [ ] Logging framework (replace print statements)

**Effort:** 10 hours

### Performance
- [ ] Lazy-load visualization dependencies
- [ ] Optimize state file I/O (currently full rewrites)
- [ ] Cache computed metrics
- [ ] Index large work block collections

**Effort:** 8 hours

### Security
- [ ] Sanitize user input in all CLI commands
- [ ] Secure token storage for OAuth
- [ ] Audit dependencies for CVEs
- [ ] Add SAST scanning

**Effort:** 6 hours

---

## Architecture Decisions

### Data Storage Evolution

**Current:** Single JSON file (`state.json`)  
**Limitations:** No concurrent access, grows unbounded, slow queries  

**Future Options:**
1. **SQLite** - Local, queryable, ACID guarantees
2. **TinyDB** - Lightweight, JSON-based with queries
3. **Git-based** - Version control built-in, good for sync

**Recommendation:** SQLite for v0.2.0

**Migration Path:**
- Add SQLite backend alongside JSON
- JSON export/import tools
- Gradual deprecation over 2-3 releases

### Plugin System

Consider extracting features into plugins:
- Visualization engines
- Calendar backends
- Focus monitors
- Storage adapters

**Benefits:** Extensibility, easier testing, community contributions  
**Drawback:** Added complexity

**Decision:** Defer until v0.3.0

---

## Documentation Needs

### User Documentation
- [x] Usage guide (USAGE_GUIDE.md)
- [ ] Video tutorials
- [ ] FAQ section
- [ ] Troubleshooting flowcharts

### Developer Documentation
- [ ] Architecture overview
- [ ] Module interaction diagrams
- [ ] Contributing guidelines
- [ ] Code style guide
- [ ] API reference (auto-generated from docstrings)

### Examples
- [ ] Sample workflows for different roles (student, developer, researcher)
- [ ] Advanced configuration examples
- [ ] Custom probe scripts
- [ ] Integration recipes

---

## Community & Release

### v0.2.0 (Target: 1 month)
- [ ] Fix all high-priority bugs
- [ ] Complete test suite
- [ ] Migration tool
- [ ] Calendar export
- [ ] SQLite backend
- [ ] Public release announcement

### v0.3.0 (Target: 3 months)
- [ ] Streamlit v2 with editing
- [ ] macOS menu bar app
- [ ] Advanced visualizations
- [ ] Plugin architecture

### v1.0.0 (Target: 6 months)
- [ ] Mobile app alpha
- [ ] AI scheduling
- [ ] Full cross-platform support
- [ ] Integration ecosystem

---

## Contributing

Priority areas for contributors:
1. **Test coverage** - Most valuable immediate help
2. **Windows/Linux testing** - Broaden platform support
3. **Visualization improvements** - Many creative options
4. **Documentation** - Always needed

See future `CONTRIBUTING.md` for detailed guidelines.

---

## Feedback Channels

*To be established:*
- [ ] GitHub Discussions
- [ ] Discord server
- [ ] Monthly user surveys
- [ ] Feature request voting

---

## Metrics to Track

Success indicators for future development:
- Daily active sessions
- Average focus score trends
- Time capsule creation rate
- Visualization generation frequency
- Feature usage analytics (opt-in)

**Current state:** No telemetry (privacy-first), manual usage tracking only

---

## Research Questions

Open questions to explore:
1. What's the optimal sprint length? (current: 2h fixed)
2. How do break patterns affect long-term productivity?
3. Can focus scores predict task completion accuracy?
4. What contextual cues best aid session resumption?

**Potential:** Academic paper on "Quantified Focus" methodology

---

*Last updated: 2025-11-13*  
*Maintainer: Seamstress Team*

