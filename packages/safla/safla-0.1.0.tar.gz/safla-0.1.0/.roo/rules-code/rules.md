# Code Mode Rules

## Overview

The Code mode is responsible for implementing, refactoring, and self-testing modular code based on specifications and prompts using SAFLA's MCP tools and CLI commands. This mode transforms refined prompts and specifications into functional, well-structured code modules with integrated tests, emphasizing MCP tool usage and CLI operations rather than direct code implementation.

## Core Responsibilities

### 1. MCP-Driven Implementation
- Use SAFLA MCP tools for code analysis, validation, and optimization
- Leverage agent-based development through MCP agent sessions
- Implement test-driven development using MCP testing tools
- Utilize meta-cognitive capabilities for self-improving code generation

### 2. CLI-Based Development Workflow
- Execute development tasks through SAFLA CLI commands
- Perform code validation and testing via command-line tools
- Monitor code quality and performance using CLI utilities
- Automate development workflows through CLI scripting

### 3. Agent-Coordinated Development
- Create specialized coding agents for different development tasks
- Coordinate multiple agents for complex implementation projects
- Use agent sessions for continuous code improvement and refactoring
- Leverage agent-based testing and validation workflows

## Implementation Guidelines

### 1. Test-First Development Using MCP Tools

#### Test Creation and Validation
```bash
# Create TDD agent for test specification
use_mcp_tool safla create_agent_session '{
  "agent_type": "cognitive",
  "session_config": {
    "focus": "test_driven_development",
    "testing_framework": "comprehensive",
    "coverage_target": 90
  },
  "timeout_seconds": 3600
}'

# Validate test specifications
use_mcp_tool safla run_integration_tests '{
  "test_suite": "tdd_specifications",
  "parallel": true,
  "verbose": true
}'
```

#### CLI-Based Test Development
```bash
# Generate test specifications via CLI
python -m safla.tdd --generate-tests \
  --spec-file phase_1_spec.md \
  --coverage-target 90 \
  --framework jest \
  --export test_specifications.json

# Validate test quality
python -m safla.test --validate \
  --test-files test_specifications.json \
  --quality-metrics coverage,maintainability,readability
```

### 2. Code Quality and Standards

#### MCP-Based Code Analysis
```bash
# Analyze code quality using MCP tools
use_mcp_tool safla analyze_performance_bottlenecks '{
  "duration_seconds": 300,
  "include_memory_profile": true
}'

# Validate code integrity
use_mcp_tool safla validate_memory_operations '{
  "test_data_size": 100,
  "include_stress_test": true
}'
```

#### CLI Code Quality Enforcement
```bash
# Run comprehensive code analysis
python -m safla.code --analyze \
  --static-analysis \
  --security-scan \
  --performance-profile \
  --export code_analysis.json

# Enforce coding standards
python -m safla.code --lint \
  --fix-auto \
  --standards typescript,security,performance \
  --export lint_report.json
```

### 3. Modular Architecture Requirements

#### File Size and Structure Limits
- No file shall exceed 500 lines of code
- Functions should be focused and under 50 lines
- Classes must follow SOLID principles
- Modules should have clear, single responsibilities

#### Documentation Standards
- Auto-document every feature using MCP tools
- Include comprehensive function and class documentation
- Maintain up-to-date README and API documentation
- Use declarative comments explaining intent and purpose

### 4. Environment and Configuration Management

#### MCP-Based Configuration
```bash
# Get system configuration
use_mcp_tool safla get_config_summary '{}'

# Validate installation and setup
use_mcp_tool safla validate_installation '{}'

# Check system status
use_mcp_tool safla get_system_info '{}'
```

#### CLI Environment Management
```bash
# Setup development environment
python -m safla.env --setup \
  --development \
  --auto-configure \
  --install-dependencies

# Validate environment configuration
python -m safla.env --validate \
  --check-dependencies \
  --verify-tools \
  --export env_status.json
```

## Development Workflow

### 1. Specification Analysis Phase

#### MCP-Driven Specification Processing
```bash
# Create specification analysis agent
use_mcp_tool safla create_agent_session '{
  "agent_type": "cognitive",
  "session_config": {
    "focus": "specification_analysis",
    "analysis_depth": "comprehensive",
    "output_format": "structured"
  }
}'

# Analyze project specifications
use_mcp_tool safla interact_with_agent '{
  "session_id": "spec_analyzer_001",
  "command": "analyze_specifications",
  "parameters": {
    "spec_files": ["phase_1_spec.md", "prompts_LS1.md"],
    "analysis_type": "implementation_ready"
  }
}'
```

#### CLI Specification Processing
```bash
# Process specification files
python -m safla.spec --analyze \
  --files phase_1_spec.md,prompts_LS1.md \
  --extract-requirements \
  --generate-tasks \
  --export spec_analysis.json

# Validate specification completeness
python -m safla.spec --validate \
  --completeness-check \
  --consistency-check \
  --export validation_report.json
```

### 2. Implementation Phase

#### Agent-Based Implementation
```bash
# Create implementation agent
use_mcp_tool safla create_agent_session '{
  "agent_type": "cognitive",
  "session_config": {
    "focus": "code_implementation",
    "language": "typescript",
    "architecture": "modular",
    "testing": "integrated"
  }
}'

# Implement core functionality
use_mcp_tool safla interact_with_agent '{
  "session_id": "impl_agent_001",
  "command": "implement_module",
  "parameters": {
    "module_name": "core_functionality",
    "test_specifications": "test_specs.json",
    "max_lines": 500
  }
}'
```

#### CLI Implementation Workflow
```bash
# Generate code scaffolding
python -m safla.code --scaffold \
  --template modular_typescript \
  --spec-file spec_analysis.json \
  --output-dir src/

# Implement with test-driven approach
python -m safla.code --implement \
  --tdd-mode \
  --test-first \
  --module-limit 500 \
  --auto-document
```

### 3. Testing and Validation Phase

#### MCP Testing Workflow
```bash
# Run comprehensive testing
use_mcp_tool safla run_integration_tests '{
  "test_suite": "implementation_validation",
  "parallel": true,
  "verbose": true
}'

# Validate implementation quality
use_mcp_tool safla validate_memory_operations '{
  "test_data_size": 200,
  "include_stress_test": true
}'

# Benchmark implementation performance
use_mcp_tool safla benchmark_memory_performance '{
  "test_duration": 180,
  "memory_patterns": ["sequential", "random", "mixed"]
}'
```

#### CLI Testing and Validation
```bash
# Execute test suite
python -m safla.test --run \
  --comprehensive \
  --coverage-report \
  --performance-metrics \
  --export test_results.json

# Validate code quality
python -m safla.code --validate \
  --quality-gates \
  --security-check \
  --performance-check \
  --export validation_results.json
```

### 4. Optimization and Refinement Phase

#### MCP-Based Optimization
```bash
# Optimize implementation performance
use_mcp_tool safla optimize_memory_usage '{
  "optimization_level": "balanced",
  "target_memory_mb": 4096
}'

# Analyze performance bottlenecks
use_mcp_tool safla analyze_performance_bottlenecks '{
  "duration_seconds": 300,
  "include_memory_profile": true
}'
```

#### CLI Optimization Workflow
```bash
# Optimize code performance
python -m safla.code --optimize \
  --performance-focus \
  --memory-efficient \
  --maintain-readability \
  --export optimization_report.json

# Refactor for maintainability
python -m safla.code --refactor \
  --extract-methods \
  --reduce-complexity \
  --improve-naming \
  --export refactor_report.json
```

## Error Handling and Recovery

### 1. MCP-Based Error Resolution

#### Error Detection and Analysis
```bash
# Monitor system health for errors
use_mcp_tool safla monitor_system_health '{
  "check_interval": 30,
  "alert_thresholds": {
    "error_rate": 5,
    "performance_degradation": 20
  }
}'

# Analyze system introspection for issues
use_mcp_tool safla analyze_system_introspection '{
  "analysis_type": "comprehensive",
  "time_window_hours": 24
}'
```

#### Automated Error Recovery
```bash
# Trigger learning cycle for error patterns
use_mcp_tool safla trigger_learning_cycle '{
  "learning_type": "reinforcement",
  "data_sources": ["error_logs", "performance_metrics"],
  "focus_areas": ["error_prevention", "code_quality"]
}'

# Update learning parameters based on errors
use_mcp_tool safla update_learning_parameters '{
  "learning_rate": 0.2,
  "adaptation_threshold": 0.1,
  "exploration_factor": 0.15
}'
```

### 2. CLI Error Handling

#### Error Detection and Reporting
```bash
# Monitor code execution for errors
python -m safla.monitor --code \
  --error-detection \
  --real-time \
  --alerts webhook:http://alerts.example.com/code

# Analyze error patterns
python -m safla.errors --analyze \
  --pattern-detection \
  --root-cause-analysis \
  --export error_analysis.json
```

#### Recovery and Correction
```bash
# Apply automated fixes
python -m safla.code --fix \
  --auto-correct \
  --safe-mode \
  --backup-original \
  --export fix_report.json

# Validate fixes
python -m safla.test --run \
  --regression-check \
  --validate-fixes \
  --export fix_validation.json
```

## Integration and Deployment

### 1. MCP Integration Workflow

#### Integration Testing
```bash
# Test MCP connectivity
use_mcp_tool safla test_mcp_connectivity '{
  "target_server": "safla",
  "test_depth": "comprehensive"
}'

# Run integration tests
use_mcp_tool safla run_integration_tests '{
  "test_suite": "code_integration",
  "parallel": true,
  "verbose": true
}'
```

#### Deployment Preparation
```bash
# Deploy code with optimization
use_mcp_tool safla deploy_safla_instance '{
  "instance_name": "code_deployment",
  "environment": "production",
  "config_overrides": {
    "code_optimization": "enabled",
    "performance_monitoring": true
  }
}'

# Monitor deployment status
use_mcp_tool safla check_deployment_status '{
  "instance_name": "code_deployment"
}'
```

### 2. CLI Integration and Deployment

#### Integration Validation
```bash
# Validate integration readiness
python -m safla.integration --validate \
  --check-dependencies \
  --verify-interfaces \
  --test-connectivity \
  --export integration_status.json

# Run integration test suite
python -m safla.test --integration \
  --comprehensive \
  --performance-check \
  --export integration_results.json
```

#### Production Deployment
```bash
# Deploy to production environment
python -m safla.deploy --production \
  --code-optimized \
  --monitoring-enabled \
  --rollback-ready \
  --export deployment_log.json

# Monitor deployment health
python -m safla.monitor --deployment \
  --real-time \
  --performance-metrics \
  --error-tracking
```

## Learning and Adaptation

### 1. Meta-Cognitive Development

#### Self-Awareness in Code Development
```bash
# Get current system awareness
use_mcp_tool safla get_system_awareness '{}'

# Update awareness for code development
use_mcp_tool safla update_awareness_state '{
  "awareness_level": 0.9,
  "focus_areas": ["code_quality", "performance", "maintainability"],
  "introspection_depth": "deep"
}'
```

#### Goal-Driven Development
```bash
# Create code quality goal
use_mcp_tool safla create_goal '{
  "goal_name": "code_quality_excellence",
  "description": "Achieve 95% code coverage and zero critical issues",
  "priority": "high",
  "target_metrics": {
    "code_coverage": 0.95,
    "critical_issues": 0,
    "performance_score": 90
  }
}'

# Evaluate progress toward goals
use_mcp_tool safla evaluate_goal_progress '{
  "goal_id": "code_quality_excellence",
  "include_recommendations": true
}'
```

### 2. Adaptive Code Improvement

#### Learning from Code Patterns
```bash
# Trigger learning cycle for code patterns
use_mcp_tool safla trigger_learning_cycle '{
  "learning_type": "meta",
  "data_sources": ["code_metrics", "performance_data", "error_patterns"],
  "focus_areas": ["code_optimization", "pattern_recognition"]
}'

# Analyze adaptation patterns
use_mcp_tool safla analyze_adaptation_patterns '{
  "pattern_type": "behavioral",
  "analysis_depth": "comprehensive",
  "time_window_days": 14
}'
```

#### Strategy Selection for Development
```bash
# Select optimal development strategy
use_mcp_tool safla select_optimal_strategy '{
  "context": "complex_module_implementation",
  "constraints": {
    "time_limit": "2_hours",
    "quality_requirements": "high",
    "performance_requirements": "optimized"
  },
  "objectives": ["maintainability", "performance", "testability"]
}'

# Create custom development strategy
use_mcp_tool safla create_custom_strategy '{
  "strategy_name": "modular_tdd_implementation",
  "description": "Test-driven modular implementation with performance optimization",
  "context": "complex_feature_development",
  "steps": [
    "analyze_specifications",
    "create_test_specifications",
    "implement_core_logic",
    "optimize_performance",
    "validate_integration"
  ],
  "expected_outcomes": ["high_quality_code", "comprehensive_tests", "optimal_performance"]
}'
```

## File Operations and Management

### 1. MCP-Based File Operations

#### File Creation and Management
```bash
# Use insert_content for new files
# Use apply_diff for updates to existing files
# Ensure all code modules are < 500 lines
# Maintain proper file organization through MCP tools

# Backup code and configuration
use_mcp_tool safla backup_safla_data '{
  "backup_type": "full",
  "destination": "/backups/code_backup.tar.gz",
  "compress": true
}'
```

#### File Validation and Integrity
```bash
# Validate file operations
use_mcp_tool safla validate_memory_operations '{
  "test_data_size": 100,
  "include_stress_test": false
}'

# Check backup status
access_mcp_resource safla "safla://backup-status"
```

### 2. CLI File Management

#### File Operations
```bash
# Create modular file structure
python -m safla.files --create-structure \
  --template modular \
  --max-lines 500 \
  --auto-organize

# Validate file integrity
python -m safla.files --validate \
  --check-size-limits \
  --verify-structure \
  --export file_validation.json
```

## Task Completion and Workflow Coordination

### 1. Workflow Coordination

#### Task Spawning and Completion
```bash
# Spawn new task for next workflow step
new_task: tdd  # For test-driven development
new_task: critic  # For code review and analysis
new_task: deployment  # For deployment preparation

# Complete current task
attempt_completion: "Code implementation completed with comprehensive testing and optimization"
```

#### Mode Integration
```bash
# Coordinate with other modes through MCP
use_mcp_tool safla create_agent_session '{
  "agent_type": "cognitive",
  "session_config": {
    "focus": "mode_coordination",
    "integration_points": ["tdd", "critic", "deployment"]
  }
}'
```

### 2. Quality Assurance and Validation

#### Final Validation
```bash
# Comprehensive final validation
use_mcp_tool safla run_integration_tests '{
  "test_suite": "comprehensive_validation",
  "parallel": true,
  "verbose": true
}'

# Performance validation
use_mcp_tool safla benchmark_memory_performance '{
  "test_duration": 300,
  "memory_patterns": ["production_simulation"]
}'
```

#### Documentation and Reporting
```bash
# Generate comprehensive documentation
python -m safla.docs --generate \
  --comprehensive \
  --api-docs \
  --usage-examples \
  --export documentation/

# Create implementation report
python -m safla.report --implementation \
  --metrics \
  --quality-assessment \
  --export implementation_report.json
```

## Security and Best Practices

### 1. Security Implementation

#### Security Validation
```bash
# Security analysis via MCP
use_mcp_tool safla analyze_performance_bottlenecks '{
  "duration_seconds": 180,
  "include_memory_profile": true
}'

# CLI security scanning
python -m safla.security --scan \
  --comprehensive \
  --vulnerability-check \
  --dependency-audit \
  --export security_report.json
```

#### Environment Security
```bash
# Avoid hardcoding secrets or environment variables
# Use secure configuration management
# Implement proper input validation and sanitization
# Follow security best practices for the target language/framework
```

### 2. Performance and Optimization

#### Performance Monitoring
```bash
# Monitor code performance
python -m safla.monitor --performance \
  --code-metrics \
  --real-time \
  --optimization-suggestions

# Benchmark code performance
python -m safla.benchmark --code \
  --comprehensive \
  --compare-baselines \
  --export performance_benchmark.json
```

This Code mode operates entirely through MCP tools and CLI commands, ensuring efficient, high-quality code development with comprehensive testing, optimization, and validation workflows.