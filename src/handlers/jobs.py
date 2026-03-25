"""
Job System Handlers
Commands: /job, /jobs, /apply, /workjob, /quitjob
"""
from aiogram import Router, types, F
from aiogram.filters import Command

from src.core.decorators import require_user, rate_limit, handle_errors
from src.services.economy_service import EconomyService
from src.core.constants import JOBS

router = Router()
economy_service = EconomyService()

# User jobs storage
user_jobs = {}
job_last_worked = {}


@router.message(Command("jobs"))
@require_user()
@rate_limit("jobs", 10, 60)
@handle_errors()
async def jobs_command(message: types.Message, db_user=None):
    """Show available jobs"""
    text = "💼 <b>Available Jobs</b>\n\n"
    
    for job_id, job in JOBS.items():
        if job_id == "unemployed":
            continue
        
        text += f"{job['emoji']} <b>{job_id.replace('_', ' ').title()}</b>\n"
        text += f"   💰 Salary: ${job['salary']}/day\n"
        
        if job['benefit']:
            text += f"   ✨ Benefit: {job['benefit']}\n"
        
        text += f"   Use <code>/apply {job_id}</code>\n\n"
    
    await message.reply(text)


@router.message(Command("job"))
@require_user()
@rate_limit("job", 10, 60)
@handle_errors()
async def job_command(message: types.Message, db_user=None):
    """Show current job"""
    if db_user.id not in user_jobs:
        return await message.reply(
            "😴 <b>You are unemployed!</b>\n\n"
            "Find a job with <code>/jobs</code> and apply with <code>/apply [job]</code>!"
        )
    
    job_id = user_jobs[db_user.id]
    job = JOBS.get(job_id, JOBS["unemployed"])
    
    text = f"{job['emoji']} <b>Your Job: {job_id.replace('_', ' ').title()}</b>\n\n"
    text += f"💰 Salary: ${job['salary']}/day\n"
    
    if job['benefit']:
        text += f"✨ Benefit: {job['benefit']}\n"
    
    text += "\n💡 Use <code>/workjob</code> to earn your salary!"
    
    await message.reply(text)


@router.message(Command("apply"))
@require_user()
@rate_limit("apply", 3, 86400)
@handle_errors()
async def apply_command(message: types.Message, db_user=None):
    """Apply for a job"""
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply(
            "❌ Usage: <code>/apply [job]</code>\n"
            "Use <code>/jobs</code> to see available jobs."
        )
    
    job_id = args[1].lower()
    
    if job_id not in JOBS:
        return await message.reply(f"❌ Job '{job_id}' not found!")
    
    if job_id == "unemployed":
        return await message.reply("❌ You can't apply to be unemployed! Use /quitjob instead.")
    
    # Check requirements
    if job_id == "baby_sitter":
        # Would check children count in production
        pass
    
    # Apply
    user_jobs[db_user.id] = job_id
    
    job = JOBS[job_id]
    
    await message.reply(
        f"🎉 <b>Job Application Accepted!</b>\n\n"
        f"{job['emoji']} You are now a {job_id.replace('_', ' ').title()}!\n"
        f"💰 Salary: ${job['salary']}/day\n\n"
        f"Use <code>/workjob</code> to earn money!"
    )


@router.message(Command("workjob"))
@require_user()
@rate_limit("workjob", 1, 86400)
@handle_errors()
async def workjob_command(message: types.Message, db_user=None):
    """Work and earn salary"""
    if db_user.id not in user_jobs:
        return await message.reply("❌ You don't have a job! Apply with /apply")
    
    job_id = user_jobs[db_user.id]
    job = JOBS.get(job_id, JOBS["unemployed"])
    
    if job_id == "unemployed":
        return await message.reply("❌ You are unemployed! Get a job with /jobs")
    
    # Give salary
    await economy_service.add_money(db_user.id, job["salary"])
    
    # Apply benefits
    benefit_text = ""
    if job_id == "doctor":
        # Would heal user in production
        benefit_text = "\n🏥 You healed yourself!"
    
    await message.reply(
        f"💼 <b>Work Complete!</b>\n\n"
        f"{job['emoji']} You worked as {job_id.replace('_', ' ').title()}\n"
        f"💰 Earned: ${job['salary']}{benefit_text}\n\n"
        f"Come back tomorrow for more work!"
    )


@router.message(Command("quitjob"))
@require_user()
@handle_errors()
async def quitjob_command(message: types.Message, db_user=None):
    """Quit current job"""
    if db_user.id not in user_jobs or user_jobs[db_user.id] == "unemployed":
        return await message.reply("❌ You don't have a job to quit!")
    
    old_job = user_jobs[db_user.id]
    user_jobs[db_user.id] = "unemployed"
    
    await message.reply(
        f"👋 <b>Job Quit!</b>\n\n"
        f"You quit your job as {old_job.replace('_', ' ').title()}.\n\n"
        f"Find a new job with <code>/jobs</code>!"
    )
