# TDD Mode Rules and Instructions

## Overview

The Test-Driven Development (TDD) mode is a specialized component of the SAFLA-aiGI integrated system that focuses exclusively on creating, managing, and optimizing comprehensive test suites through MCP tools and CLI commands. This mode operates as the testing orchestrator within the aiGI framework, ensuring high-quality, maintainable, and comprehensive test coverage for all development activities.

## Core Responsibilities

### 1. Test Specification and Design

The TDD mode is responsible for creating comprehensive test specifications that serve as contracts for implementation:

#### Test Strategy Development
- **MCP Integration**: Use [`create_agent_session`](safla/mcp_stdio_server.py:1) with testing-focused cognitive agents
- **CLI Operations**: Execute `python -m safla.tdd --strategy` commands for test planning
- **Resource Access**: Monitor test strategies via [`safla://test-results`](safla/mcp_stdio_server.py:1)
- **Goal Management**: Create testing goals using [`create_goal`](safla/mcp_stdio_server.py:1) for coverage and quality targets

#### Test Case Generation
- **Automated Generation**: Use [`interact_with_agent`](safla/mcp_stdio_server.py:1) for AI-powered test case creation
- **Specification Analysis**: Process requirements through `python -m safla.spec --analyze` commands
- **Coverage Planning**: Implement comprehensive coverage strategies via CLI tools
- **Edge Case Identification**: Leverage MCP tools for boundary condition analysis

### 2. Test Implementation and Execution

#### Test Framework Integration
- **Framework Setup**: Configure testing frameworks through `python -m safla.env --setup` commands
- **Test Execution**: Run tests via [`run_integration_tests`](safla/mcp_stdio_server.py:1) MCP tool
- **Parallel Processing**: Execute `python -m safla.test --parallel` for efficient test runs
- **Result Validation**: Access results through [`safla://test-results`](safla/mcp_stdio_server.py:1) resource

#### Quality Assurance
- **Coverage Analysis**: Monitor coverage via [`safla://test-coverage`](safla/mcp_stdio_server.py:1) resource
- **Performance Testing**: Use [`benchmark_memory_performance`](safla/mcp_stdio_server.py:1) for performance validation
- **Memory Validation**: Execute [`validate_memory_operations`](safla/mcp_stdio_server.py:1) for memory integrity
- **Integration Testing**: Coordinate with other modes through agent sessions

### 3. Adaptive Test Optimization

#### Learning-Based Test Enhancement
- **Pattern Recognition**: Use [`trigger_learning_cycle`](safla/mcp_stdio_server.py:1) for test pattern analysis
- **Strategy Optimization**: Apply [`select_optimal_strategy`](safla/mcp_stdio_server.py:1) for test approach selection
- **Continuous Improvement**: Monitor [`safla://learning-metrics`](safla/mcp_stdio_server.py:1) for test effectiveness
- **Adaptation Tracking**: Analyze [`safla://adaptation-patterns`](safla/mcp_stdio_server.py:1) for test evolution

#### Meta-Cognitive Test Analysis
- **Self-Reflection**: Use [`analyze_system_introspection`](safla/mcp_stdio_server.py:1) for test quality assessment
- **Awareness Updates**: Apply [`update_awareness_state`](safla/mcp_stdio_server.py:1) for testing focus areas
- **Goal Evaluation**: Monitor [`evaluate_goal_progress`](safla/mcp_stdio_server.py:1) for testing objectives
- **Strategy Creation**: Develop [`create_custom_strategy`](safla/mcp_stdio_server.py:1) for specialized testing approaches

## Operational Guidelines

### 1. Test-First Development Approach

#### Red-Green-Refactor Cycle Implementation
```bash
# Red Phase: Create failing tests
use_mcp_tool safla create_agent_session '{
  "agent_type": "cognitive",
  "session_config": {
    "focus": "test_creation",
    "testing_framework": "jest",
    "coverage_target": 95
  }
}'

# Green Phase: Coordinate with code mode
new_task: code  # Spawn implementation task

# Refactor Phase: Optimize tests
python -m safla.test --optimize --refactor
```

#### Test Specification as Contracts
- **Behavioral Specifications**: Define expected behaviors through comprehensive test cases
- **Interface Contracts**: Establish clear API contracts through interface testing
- **Performance Contracts**: Set performance expectations through benchmark tests
- **Error Handling Contracts**: Define error scenarios and expected responses

### 2. Comprehensive Testing Strategies

#### Multi-Level Testing Approach
- **Unit Testing**: Focus on individual component behavior and functionality
- **Integration Testing**: Validate component interactions and data flow
- **System Testing**: Ensure end-to-end functionality and user workflows
- **Performance Testing**: Validate system performance under various conditions

#### Quality Metrics and Targets
- **Coverage Targets**: Maintain minimum 95% line and branch coverage
- **Quality Gates**: Implement automated quality validation checkpoints
- **Performance Benchmarks**: Establish and maintain performance baselines
- **Maintainability Metrics**: Track test maintainability and readability scores

### 3. Agent Coordination and Collaboration

#### Multi-Agent Testing Coordination
```bash
# Create specialized testing agents
python -m safla.agents --batch-create \
  --agents unit_test,integration_test,performance_test \
  --coordinate --monitor

# Coordinate with implementation agents
use_mcp_tool safla list_agent_sessions '{
  "filter_by_type": "cognitive"
}'
```

#### Cross-Mode Integration
- **Code Mode Collaboration**: Provide test specifications for implementation
- **Critic Mode Integration**: Supply test results for quality analysis
- **Orchestrator Coordination**: Report testing status and progress
- **Memory Manager Integration**: Validate memory operations and performance

## Error Handling and Recovery

### 1. Test Failure Analysis and Resolution

#### Automated Failure Analysis
```bash
# Analyze test failure patterns
python -m safla.test --analyze-failures \
  --pattern-detection \
  --root-cause-analysis

# Use MCP for failure pattern learning
use_mcp_tool safla trigger_learning_cycle '{
  "learning_type": "reinforcement",
  "data_sources": ["test_failures", "error_patterns"],
  "focus_areas": ["failure_prevention", "test_reliability"]
}'
```

#### Recovery Strategies
- **Automatic Retry**: Implement intelligent test retry mechanisms
- **Flaky Test Detection**: Identify and address unreliable tests
- **Environment Validation**: Ensure test environment consistency
- **Dependency Management**: Validate and manage test dependencies

### 2. Performance and Memory Testing

#### Memory Operation Validation
```bash
# Validate memory operations through MCP
use_mcp_tool safla validate_memory_operations '{
  "test_data_size": 100,
  "include_stress_test": true
}'

# Monitor memory performance during testing
use_mcp_tool safla analyze_performance_bottlenecks '{
  "duration_seconds": 300,
  "include_memory_profile": true
}'
```

#### Performance Regression Detection
- **Baseline Establishment**: Create and maintain performance baselines
- **Regression Monitoring**: Detect performance degradations early
- **Optimization Validation**: Verify performance improvements
- **Resource Usage Tracking**: Monitor system resource consumption

## Integration Patterns

### 1. MCP Tool Integration

#### Primary MCP Tools for TDD Mode
- **Agent Management**: [`create_agent_session`](safla/mcp_stdio_server.py:1), [`interact_with_agent`](safla/mcp_stdio_server.py:1), [`list_agent_sessions`](safla/mcp_stdio_server.py:1)
- **Testing Tools**: [`run_integration_tests`](safla/mcp_stdio_server.py:1), [`validate_memory_operations`](safla/mcp_stdio_server.py:1), [`test_mcp_connectivity`](safla/mcp_stdio_server.py:1)
- **Performance Tools**: [`benchmark_memory_performance`](safla/mcp_stdio_server.py:1), [`benchmark_vector_operations`](safla/mcp_stdio_server.py:1), [`analyze_performance_bottlenecks`](safla/mcp_stdio_server.py:1)
- **Learning Tools**: [`trigger_learning_cycle`](safla/mcp_stdio_server.py:1), [`get_learning_metrics`](safla/mcp_stdio_server.py:1), [`analyze_adaptation_patterns`](safla/mcp_stdio_server.py:1)

#### Resource Access Patterns
- **Test Results**: [`safla://test-results`](safla/mcp_stdio_server.py:1) for real-time test execution data
- **Coverage Metrics**: [`safla://test-coverage`](safla/mcp_stdio_server.py:1) for coverage analysis
- **Performance Data**: [`safla://performance-metrics`](safla/mcp_stdio_server.py:1) for performance testing
- **Learning Insights**: [`safla://learning-metrics`](safla/mcp_stdio_server.py:1) for adaptive improvement

### 2. CLI Command Integration

#### Core CLI Operations
```bash
# Test environment setup
python -m safla.env --setup --testing --framework jest

# Test generation and execution
python -m safla.tdd --generate --comprehensive
python -m safla.test --run --parallel --coverage

# Performance and validation
python -m safla.benchmark --testing --comprehensive
python -m safla.validate --test-quality --coverage-check
```

#### Advanced CLI Workflows
- **Automated Test Generation**: `python -m safla.tdd --auto-generate`
- **Coverage Analysis**: `python -m safla.coverage --analyze --report`
- **Performance Testing**: `python -m safla.performance --test --benchmark`
- **Quality Validation**: `python -m safla.quality --test-validation`

## Workflow Coordination

### 1. Task Spawning and Completion

#### Workflow Integration Points
```bash
# Spawn related tasks
new_task: code      # For implementation based on tests
new_task: critic    # For test quality analysis
new_task: orchestrator  # For workflow coordination

# Complete TDD tasks
attempt_completion: "Test suite completed with 96% coverage and comprehensive validation"
```

#### Handoff Protocols
- **Test Specifications**: Provide comprehensive test specifications to code mode
- **Quality Reports**: Supply test quality analysis to critic mode
- **Performance Data**: Share performance test results with optimization modes
- **Learning Insights**: Contribute test patterns to meta-cognitive engine

### 2. Continuous Integration

#### CI/CD Integration
```bash
# Setup automated testing in CI/CD
python -m safla.cicd --configure --testing-focus
python -m safla.automation --testing --comprehensive

# Monitor CI/CD test execution
access_mcp_resource safla "safla://test-results"
```

#### Quality Gates
- **Coverage Gates**: Enforce minimum coverage requirements
- **Performance Gates**: Validate performance benchmarks
- **Quality Gates**: Ensure code quality through testing
- **Security Gates**: Validate security through security testing

## Best Practices and Standards

### 1. Test Design Principles

#### FIRST Principles
- **Fast**: Tests should execute quickly and efficiently
- **Independent**: Tests should not depend on other tests
- **Repeatable**: Tests should produce consistent results
- **Self-Validating**: Tests should have clear pass/fail criteria
- **Timely**: Tests should be written at the appropriate time

#### Test Structure Standards
- **Arrange-Act-Assert**: Follow AAA pattern for test organization
- **Descriptive Naming**: Use clear, descriptive test names
- **Single Responsibility**: Each test should validate one behavior
- **Comprehensive Coverage**: Cover positive, negative, and edge cases

### 2. Quality Assurance

#### Test Quality Metrics
```bash
# Monitor test quality through MCP
use_mcp_tool safla get_learning_metrics '{
  "metric_type": "all",
  "time_range_hours": 24
}'

# Analyze test effectiveness
python -m safla.test --quality-analysis --metrics all
```

#### Continuous Improvement
- **Regular Review**: Periodically review and update test suites
- **Pattern Analysis**: Identify and apply successful testing patterns
- **Tool Optimization**: Continuously improve testing tools and processes
- **Knowledge Sharing**: Document and share testing best practices

## Security and Compliance

### 1. Security Testing Integration

#### Security Validation
```bash
# Security testing through CLI
python -m safla.security --test --comprehensive
python -m safla.vulnerability --scan --testing-focus

# Validate security through MCP
use_mcp_tool safla run_integration_tests '{
  "test_suite": "security_validation",
  "parallel": true
}'
```

#### Compliance Testing
- **Regulatory Compliance**: Ensure tests meet regulatory requirements
- **Security Standards**: Validate against security testing standards
- **Quality Standards**: Maintain compliance with quality standards
- **Documentation Requirements**: Ensure proper test documentation

### 2. Data Protection and Privacy

#### Test Data Management
- **Synthetic Data**: Use synthetic data for testing when possible
- **Data Anonymization**: Ensure test data is properly anonymized
- **Access Controls**: Implement proper access controls for test data
- **Retention Policies**: Follow data retention policies for test data

## Performance Optimization

### 1. Test Execution Optimization

#### Parallel Execution
```bash
# Optimize test execution through MCP
use_mcp_tool safla optimize_memory_usage '{
  "optimization_level": "balanced",
  "target_memory_mb": 4096
}'

# Parallel test execution
python -m safla.test --parallel --optimize --efficient
```

#### Resource Management
- **Memory Optimization**: Optimize memory usage during test execution
- **CPU Utilization**: Maximize CPU utilization for test execution
- **I/O Optimization**: Optimize I/O operations for test efficiency
- **Network Optimization**: Optimize network usage for distributed testing

### 2. Test Suite Maintenance

#### Automated Maintenance
```bash
# Automated test maintenance
python -m safla.test --maintain --optimize --cleanup
python -m safla.automation --test-maintenance

# Learning-based optimization
use_mcp_tool safla trigger_learning_cycle '{
  "learning_type": "meta",
  "focus_areas": ["test_optimization", "maintenance_efficiency"]
}'
```

#### Continuous Optimization
- **Performance Monitoring**: Monitor test execution performance
- **Bottleneck Identification**: Identify and resolve test bottlenecks
- **Resource Optimization**: Optimize resource usage for testing
- **Scalability Planning**: Plan for test suite scalability

This comprehensive TDD mode documentation ensures effective test-driven development through systematic use of SAFLA's MCP tools and CLI commands, emphasizing quality, performance, and continuous improvement in testing practices.