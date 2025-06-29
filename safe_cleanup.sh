#!/bin/bash
# Safe step-by-step cleanup script

echo "🧹 Safe Cleanup Script for Next Gen Workflow"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Confirmation function
confirm() {
    read -p "$1 [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    fi
    return 1
}

# Step 1: Create full backup
echo -e "${YELLOW}Step 1: Creating full project backup${NC}"
BACKUP_NAME="project_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
if confirm "Create full backup to $BACKUP_NAME?"; then
    tar -czf "$BACKUP_NAME" --exclude='node_modules' --exclude='.git' --exclude='*.tar.gz' .
    echo -e "${GREEN}✓ Backup created: $BACKUP_NAME${NC}"
else
    echo -e "${RED}⚠️  Skipping backup (not recommended)${NC}"
fi

# Step 2: Clean temporary files
echo -e "\n${YELLOW}Step 2: Remove temporary files${NC}"
echo "Files to remove:"
echo "  - .DS_Store files"
echo "  - *.bak and *.backup files"
if confirm "Remove these temporary files?"; then
    find . -name ".DS_Store" -delete
    find . -name "*.bak" -o -name "*.backup" -delete
    echo -e "${GREEN}✓ Temporary files removed${NC}"
fi

# Step 3: Clean duplicate Discord bot files
echo -e "\n${YELLOW}Step 3: Remove duplicate Discord bot files${NC}"
echo "Will keep: src/discord_bot.py"
echo "Will remove:"
for file in src/discord_bot_original.py src/discord_bot_debug.py src/discord_bot_ultra_simple.py src/discord_bot_simple_no_buttons.py src/discord_bot_step1.py debug_bot_simple.py; do
    if [ -f "$file" ]; then
        echo "  - $file"
    fi
done
if confirm "Remove these duplicate Discord bot files?"; then
    rm -f src/discord_bot_original.py
    rm -f src/discord_bot_debug.py
    rm -f src/discord_bot_ultra_simple.py
    rm -f src/discord_bot_simple_no_buttons.py
    rm -f src/discord_bot_step1.py
    rm -f debug_bot_simple.py
    echo -e "${GREEN}✓ Discord bot duplicates removed${NC}"
fi

# Step 4: Move test files
echo -e "\n${YELLOW}Step 4: Organize test files${NC}"
echo "Will move test files from root to tests/"
if confirm "Move test files to tests/ directory?"; then
    mkdir -p tests
    for file in test_*.py simple_blog_test.py intent_test.py; do
        if [ -f "$file" ]; then
            mv "$file" tests/
            echo "  Moved: $file → tests/$file"
        fi
    done
    echo -e "${GREEN}✓ Test files organized${NC}"
fi

# Step 5: Clean old job logs
echo -e "\n${YELLOW}Step 5: Clean old job logs${NC}"
if [ -d "data/job_logs" ]; then
    OLD_LOGS=$(ls -t data/job_logs/*.db 2>/dev/null | tail -n +6 | wc -l)
    echo "Found $OLD_LOGS old job logs (keeping 5 most recent)"
    if [ "$OLD_LOGS" -gt 0 ] && confirm "Remove old job logs?"; then
        cd data/job_logs && ls -t *.db | tail -n +6 | xargs rm -f
        cd ../..
        echo -e "${GREEN}✓ Old job logs cleaned${NC}"
    fi
fi

# Step 6: Clean duplicate mockups
echo -e "\n${YELLOW}Step 6: Remove duplicate mockups${NC}"
if [ -d "archive/mockups_complete_2025_06_26" ]; then
    echo "Duplicate mockups directory size: $(du -sh archive/mockups_complete_2025_06_26/ | cut -f1)"
    if confirm "Remove archive/mockups_complete_2025_06_26/?"; then
        rm -rf archive/mockups_complete_2025_06_26
        echo -e "${GREEN}✓ Duplicate mockups removed${NC}"
    fi
fi

# Step 7: Clean Claude auth fix files
echo -e "\n${YELLOW}Step 7: Clean Claude auth fix temporary files${NC}"
echo "Files to remove:"
echo "  - CLAUDE_AUTH_FIX_REPORT.md"
echo "  - CLAUDE_AUTH_FIX_SUMMARY.md"
echo "  - claude_auth_migration_guide.md"
echo "  - fix_claude_auth_commands.sh"
echo "  - fix_claude_auth_references.py"
if confirm "Remove these temporary Claude auth fix files?"; then
    rm -f CLAUDE_AUTH_FIX_REPORT.md
    rm -f CLAUDE_AUTH_FIX_SUMMARY.md
    rm -f claude_auth_migration_guide.md
    rm -f fix_claude_auth_commands.sh
    rm -f fix_claude_auth_references.py
    echo -e "${GREEN}✓ Claude auth fix files removed${NC}"
fi

# Step 8: Create organized structure
echo -e "\n${YELLOW}Step 8: Create better directory structure${NC}"
if confirm "Create organized directory structure?"; then
    # Create directories
    mkdir -p scripts/{setup,maintenance,testing}
    mkdir -p docs/{setup,development,architecture,guides}
    mkdir -p config
    
    # Move files if they exist
    [ -f "deploy_fast_blog.sh" ] && mv deploy_fast_blog.sh scripts/setup/
    [ -f "quick_test_v2.sh" ] && mv quick_test_v2.sh scripts/testing/
    [ -f "docker_quick_start.sh" ] && mv docker_quick_start.sh scripts/setup/
    
    # Move notification scripts
    for file in send_*_notification.py; do
        [ -f "$file" ] && mv "$file" scripts/maintenance/
    done
    
    # Move config files
    [ -f "notification_config.json" ] && mv notification_config.json config/
    [ -f "discord_bot_config.json" ] && mv discord_bot_config.json config/
    
    echo -e "${GREEN}✓ Directory structure improved${NC}"
fi

echo -e "\n${GREEN}=== Cleanup Complete ===${NC}"
echo "Next steps:"
echo "1. Test core functionality"
echo "2. Commit changes: git add -A && git commit -m 'Clean up and reorganize project structure'"
echo "3. Push changes: git push origin main"