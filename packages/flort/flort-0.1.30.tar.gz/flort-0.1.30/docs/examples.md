# Examples Guide

Real-world examples and use cases for Flort across different project types and workflows.

## 🐍 Python Projects

### Django Web Application

```bash
# Complete Django project analysis
flort . \
  --extensions py,html,css,js,md \
  --exclude-patterns "*migration*,*test*,*cache*,*.min.*" \
  --ignore-dirs "venv,staticfiles,media,.git,__pycache__" \
  --include-files "manage.py,requirements.txt,settings.py" \
  --outline \
  --output django_analysis.txt
```

**What this captures:**
- Python models, views, forms
- HTML templates
- CSS and JavaScript assets
- Documentation files
- Key configuration files
- Excludes migrations and test files

### Python Package Development

```bash
# Package structure for PyPI submission
flort . \
  --extensions py,md,txt,cfg,ini,toml \
  --include-files "setup.py,pyproject.toml,MANIFEST.in,LICENSE" \
  --ignore-dirs "build,dist,*.egg-info,.git,venv" \
  --outline \
  --archive zip \
  --output package_source.txt
```

### Data Science Project

```bash
# Jupyter notebooks and Python scripts
flort . \
  --extensions py,ipynb,md,yml \
  --include-files "requirements.txt,environment.yml,README.md" \
  --ignore-dirs "data,models,.ipynb_checkpoints,venv" \
  --exclude-patterns "*checkpoint*,*cache*" \
  --output data_project.txt
```

### FastAPI Application

```bash
# API documentation and code
flort . \
  --extensions py,md,yml,json \
  --include-files "main.py,requirements.txt,docker-compose.yml" \
  --exclude-patterns "*test*,*cache*" \
  --ignore-dirs "venv,.pytest_cache" \
  --outline \
  --output fastapi_docs.txt
```

## 🌐 Web Development

### React Application

```bash
# Modern React project
flort src/ public/ \
  --extensions js,jsx,ts,tsx,css,scss,json,md \
  --exclude-patterns "*.min.*,*bundle*,*build*,*test*" \
  --ignore-dirs "node_modules,build,dist,.cache" \
  --include-files "package.json,package-lock.json,README.md" \
  --output react_app.txt
```

### Vue.js Project

```bash
# Vue application with configuration
flort . \
  --extensions vue,js,ts,css,scss,json,md \
  --exclude-patterns "*.min.*,*bundle*,*dist*,*test*" \
  --ignore-dirs "node_modules,dist,build" \
  --include-files "package.json,vue.config.js,vite.config.js" \
  --output vue_project.txt
```

### Full-Stack MEAN/MERN

```bash
# Complete full-stack application
flort . \
  --extensions js,ts,jsx,tsx,css,scss,json,md,html \
  --exclude-patterns "*.min.*,*bundle*,*build*,*test*,*spec*" \
  --ignore-dirs "node_modules,build,dist,coverage" \
  --include-files "package.json,server.js,app.js,index.html" \
  --max-depth 4 \
  --output fullstack_app.txt
```

### Static Site (Jekyll/Hugo)

```bash
# Static site generator project
flort . \
  --extensions md,html,css,scss,js,yml,yaml \
  --include-files "_config.yml,config.toml,Gemfile,package.json" \
  --ignore-dirs "_site,public,node_modules,.git" \
  --exclude-patterns "*cache*,*build*" \
  --output static_site.txt
```

## ☕ Java Projects

### Spring Boot Application

```bash
# Enterprise Spring Boot project
flort . \
  --extensions java,xml,properties,yml,md \
  --exclude-patterns "*Test*,*test*" \
  --ignore-dirs "target,build,.gradle,.idea" \
  --include-files "pom.xml,build.gradle,application.properties" \
  --max-depth 5 \
  --output spring_boot_app.txt
```

### Android Application

```bash
# Android app source code
flort app/src/ \
  --extensions java,kt,xml,gradle,md \
  --exclude-patterns "*test*,*Test*,*androidTest*" \
  --include-files "build.gradle,AndroidManifest.xml,proguard-rules.pro" \
  --ignore-dirs "build,.gradle" \
  --output android_app.txt
```

### Maven Multi-Module Project

```bash
# Large Maven project
flort . \
  --extensions java,xml,properties,md \
  --exclude-patterns "*test*,*Test*" \
  --ignore-dirs "target,.idea,.settings" \
  --include-files "pom.xml,README.md" \
  --max-depth 3 \
  --output maven_project.txt
```

## 🔧 DevOps and Infrastructure

### Docker Multi-Service Setup

```bash
# Containerized application
flort . \
  --extensions yml,yaml,dockerfile,sh,md,env \
  --include-files "Dockerfile,docker-compose.yml,.env.example" \
  --exclude-patterns "*cache*,*log*" \
  --ignore-dirs ".git,node_modules,venv" \
  --output docker_setup.txt
```

### Kubernetes Configuration

```bash
# K8s deployment configs
flort k8s/ deploy/ \
  --extensions yml,yaml,json,md \
  --include-files "kustomization.yaml,values.yaml" \
  --exclude-patterns "*secret*" \
  --output k8s_config.txt
```

### Terraform Infrastructure

```bash
# Infrastructure as Code
flort . \
  --extensions tf,tfvars,hcl,md \
  --include-files "terraform.tf,variables.tf,outputs.tf" \
  --exclude-patterns "*.tfstate*,*cache*" \
  --ignore-dirs ".terraform,terraform.tfstate.d" \
  --output terraform_config.txt
```

### Ansible Playbooks

```bash
# Configuration management
flort . \
  --extensions yml,yaml,j2,md \
  --include-files "ansible.cfg,inventory,requirements.yml" \
  --ignore-dirs "roles/downloaded,.git" \
  --exclude-patterns "*vault*,*secret*" \
  --output ansible_playbooks.txt
```

## 📊 Data and Analytics

### Machine Learning Project

```bash
# ML pipeline and experiments
flort . \
  --extensions py,ipynb,yml,json,md \
  --include-files "requirements.txt,environment.yml,setup.py" \
  --ignore-dirs "data,models,logs,mlruns,.ipynb_checkpoints" \
  --exclude-patterns "*checkpoint*,*cache*,*.pkl,*.h5" \
  --outline \
  --output ml_project.txt
```

### Data Engineering Pipeline

```bash
# ETL and data processing
flort . \
  --extensions py,sql,yml,json,md \
  --include-files "airflow.cfg,dbt_project.yml,requirements.txt" \
  --ignore-dirs "logs,data,venv,.pytest_cache" \
  --exclude-patterns "*test*,*cache*,*.parquet,*.csv" \
  --outline \
  --output data_pipeline.txt
```

## 📱 Mobile Development

### React Native App

```bash
# Cross-platform mobile app
flort . \
  --extensions js,jsx,ts,tsx,json,md \
  --exclude-patterns "*.bundle.*,*build*,*test*" \
  --ignore-dirs "node_modules,ios/build,android/build" \
  --include-files "package.json,app.json,metro.config.js" \
  --output react_native_app.txt
```

### Flutter Application

```bash
# Dart/Flutter project
flort . \
  --extensions dart,yaml,md \
  --exclude-patterns "*test*,*generated*" \
  --ignore-dirs "build,.dart_tool,.idea" \
  --include-files "pubspec.yaml,analysis_options.yaml" \
  --output flutter_app.txt
```

## 🔬 Research and Academic

### Research Paper with Code

```bash
# Academic project with implementation
flort . \
  --extensions py,r,md,tex,bib,yml \
  --include-files "README.md,requirements.txt,environment.yml" \
  --ignore-dirs "data,results,figures,venv,.git" \
  --exclude-patterns "*cache*,*.aux,*.log" \
  --outline \
  --output research_project.txt
```

### Thesis Project

```bash
# LaTeX thesis with supporting code
flort . \
  --extensions tex,bib,py,r,md \
  --include-files "main.tex,references.bib,Makefile" \
  --exclude-patterns "*.aux,*.log,*.pdf,*cache*" \
  --ignore-dirs "figures,data,venv" \
  --output thesis_project.txt
```

## 📚 Documentation Projects

### Technical Documentation Site

```bash
# MkDocs or similar documentation
flort . \
  --extensions md,yml,css,js \
  --include-files "mkdocs.yml,requirements.txt,README.md" \
  --ignore-dirs "site,venv,node_modules,.git" \
  --exclude-patterns "*cache*,*build*" \
  --output docs_site.txt
```

### API Documentation

```bash
# OpenAPI/Swagger documentation
flort . \
  --extensions yml,yaml,json,md \
  --include-files "openapi.yml,swagger.json,README.md" \
  --exclude-patterns "*build*,*cache*" \
  --output api_docs.txt
```

## 🎯 Specialized Use Cases

### LLM Context Preparation

```bash
# Clean code context for AI assistance
flort . \
  --extensions py,md \
  --exclude-patterns "*test*,*spec*,*cache*,*__pycache__*" \
  --ignore-dirs "venv,.git,build,dist,.pytest_cache" \
  --outline \
  --max-depth 3 \
  --output llm_context.txt
```

### Code Review Package

```bash
# Package changed files for review
CHANGED_FILES=$(git diff --name-only HEAD~5..HEAD | tr '\n' ',')
flort . \
  --include-files "$CHANGED_FILES" \
  --outline \
  --archive zip \
  --output "code_review_$(date +%Y%m%d).txt"
```

### Security Audit Preparation

```bash
# Focus on configuration and security-relevant files
flort . \
  --extensions py,js,json,yml,env,conf,cfg \
  --include-files ".env.example,docker-compose.yml,nginx.conf" \
  --exclude-patterns "*test*,*cache*,*build*" \
  --ignore-dirs "venv,node_modules,.git" \
  --output security_audit.txt
```

### Deployment Package

```bash
# Production deployment files
flort . \
  --extensions py,yml,json,sh,dockerfile \
  --include-files "requirements.txt,docker-compose.yml,Dockerfile" \
  --exclude-patterns "*test*,*dev*,*cache*" \
  --ignore-dirs "venv,tests,.git,__pycache__" \
  --archive tar.gz \
  --output deployment_package.txt
```

## 🔄 Workflow Integration

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Generate current project state
flort . \
  --extensions py,js,md \
  --exclude-patterns "*test*,*cache*" \
  --outline \
  --output .git/hooks/current_state.txt

echo "Project snapshot updated in .git/hooks/current_state.txt"
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/documentation.yml
name: Generate Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Flort
        run: pip install flort
      - name: Generate Project Overview
        run: |
          flort . \
            --extensions py,md,yml \
            --exclude-patterns "*test*,*cache*" \
            --outline \
            --output docs/project_overview.txt
      - name: Commit Documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/project_overview.txt
          git commit -m "Update project overview" || exit 0
          git push
```

### Makefile Integration

```makefile
# Makefile

.PHONY: docs review package

# Generate documentation
docs:
	flort . \
		--extensions py,md,yml \
		--exclude-patterns "*test*,*cache*" \
		--outline \
		--output docs/api_overview.txt

# Create code review package
review:
	flort . \
		--include-files $(shell git diff --name-only HEAD~1) \
		--archive zip \
		--output review_$(shell date +%Y%m%d_%H%M).txt

# Package for distribution
package:
	flort . \
		--extensions py,md,txt,yml \
		--include-files "setup.py,requirements.txt,LICENSE" \
		--ignore-dirs "build,dist,venv,.git" \
		--archive tar.gz \
		--output dist/source_package.txt
```

### Shell Script Automation

```bash
#!/bin/bash
# auto_flort.sh - Intelligent project analysis

PROJECT_DIR="${1:-.}"
PROJECT_NAME=$(basename $(realpath $PROJECT_DIR))
OUTPUT_DIR="${2:-./flort_output}"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Analyzing project: $PROJECT_NAME"

# Detect project type and apply appropriate filters
if [ -f "$PROJECT_DIR/package.json" ]; then
    echo "📦 Detected Node.js project"
    flort "$PROJECT_DIR" \
        --extensions js,ts,jsx,tsx,json,md \
        --ignore-dirs "node_modules,build,dist" \
        --exclude-patterns "*.min.*,*bundle*" \
        --include-files "package.json,README.md" \
        --output "$OUTPUT_DIR/${PROJECT_NAME}_nodejs.txt"
        
elif [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/setup.py" ]; then
    echo "🐍 Detected Python project"
    flort "$PROJECT_DIR" \
        --extensions py,md,yml,txt \
        --ignore-dirs "venv,__pycache__,.pytest_cache" \
        --exclude-patterns "*test*,*.pyc" \
        --include-files "requirements.txt,setup.py,README.md" \
        --outline \
        --output "$OUTPUT_DIR/${PROJECT_NAME}_python.txt"
        
elif [ -f "$PROJECT_DIR/pom.xml" ] || [ -f "$PROJECT_DIR/build.gradle" ]; then
    echo "☕ Detected Java project"
    flort "$PROJECT_DIR" \
        --extensions java,xml,properties,md \
        --ignore-dirs "target,build,.idea" \
        --exclude-patterns "*test*,*Test*" \
        --include-files "pom.xml,build.gradle" \
        --output "$OUTPUT_DIR/${PROJECT_NAME}_java.txt"
        
else
    echo "❓ Unknown project type, using generic analysis"
    flort "$PROJECT_DIR" \
        --all \
        --ignore-dirs ".git,node_modules,venv,build,dist" \
        --exclude-patterns "*cache*,*build*,*.min.*" \
        --output "$OUTPUT_DIR/${PROJECT_NAME}_generic.txt"
fi

echo "✅ Analysis complete: $OUTPUT_DIR/"
```

## 📈 Performance Examples

### Large Codebase Optimization

```bash
# For very large projects, use staged approach
# Stage 1: Quick overview
flort . --all --manifest --max-depth 2 --output overview.txt

# Stage 2: Specific components
flort src/ --extensions py,js --outline --output core_code.txt
flort docs/ --extensions md --output documentation.txt

# Stage 3: Configuration files
flort . --include-files "package.json,requirements.txt,Dockerfile" --output config.txt
```

### Memory-Efficient Processing

```bash
# Process directories separately for memory efficiency
for dir in src tests docs; do
    if [ -d "$dir" ]; then
        flort "$dir" \
            --extensions py,md \
            --exclude-patterns "*cache*" \
            --output "${dir}_analysis.txt"
    fi
done

# Combine results if needed
cat *_analysis.txt > complete_analysis.txt
```

## 🎨 Creative Use Cases

### Project Archaeology

```bash
# Analyze project evolution over time
git log --oneline | head -10 | while read commit message; do
    git checkout $commit
    flort . --extensions py --manifest --output "history_${commit}.txt"
done
git checkout main
```

### Dependency Analysis

```bash
# Focus on import/require statements
flort . \
    --extensions py,js,json \
    --include-files "requirements.txt,package.json,setup.py" \
    --output dependencies.txt

# Then grep for imports
grep -E "(import|require|from)" dependencies.txt > imports_analysis.txt
```

### License Compliance

```bash
# Gather all license-related files
flort . \
    --extensions md,txt \
    --include-files "LICENSE,COPYING,NOTICE,COPYRIGHT" \
    --glob "*license*,*LICENSE*,*copyright*" \
    --output license_audit.txt
```

---

These examples should give you a solid foundation for using Flort in various real-world scenarios. Remember to adjust the filters based on your specific project structure and requirements!

---
