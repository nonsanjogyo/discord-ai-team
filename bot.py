import os
import asyncio
import discord
from anthropic import Anthropic

# Anthropic 클라이언트 초기화
claude = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 각 봇별 설정 (토큰 환경변수명, 기본 역할)
BOT_CONFIGS = [
    {
        "env": "DISCORD_TOKEN_SALES",
        "name": "영업 매니저",
        "role": "당신은 전문 B2B IT 솔루션 영업 매니저입니다. 고객 응대, 제안 전략 수립, 세일즈 파이프라인 관리를 전문적이고 정중하게 지원합니다."
    },
    {
        "env": "DISCORD_TOKEN_MARKETING",
        "name": "마케팅 매니저",
        "role": "당신은 B2B SaaS 및 IT 테크 전문 마케팅 매니저입니다. 콘텐츠 기획, 카피라이팅, 캠페인 전략을 창의적이고 설득력 있게 제시합니다."
    },
    {
        "env": "DISCORD_TOKEN_PM",
        "name": "기획 매니저",
        "role": "당신은 노련한 IT 프로덕트 매니저(PM)입니다. 기능 명세서(PRD) 작성, 유저 플로우 도출, 요구사항 분석을 구조화된 표와 불릿 포인트로 작성합니다."
    },
    {
        "env": "DISCORD_TOKEN_LEGAL",
        "name": "법무 검토관",
        "role": "당신은 기업 법무 검토 전문가입니다. 계약서 조항, 메일 문구의 법적 리스크 분석, 책임 제한 조항 검토, 독소 조항 방어를 매우 객관적이고 신중하게 자문합니다."
    },
    {
        "env": "DISCORD_TOKEN_TECH",
        "name": "기술 지원팀",
        "role": "당신은 시니어 시스템 아키텍트이자 기술 지원 엔지니어입니다. API 연동, 데이터 아키텍처, 기술적 제약 사항을 명확하고 기술적으로 설명합니다. 설명은 10대 학생에게 하는 수준으로 쉽고, 명로하게 합니다. "
    }
]

def make_client(config):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"[{config['name']}] 정상 로그인 완료: {client.user}")

    @client.event
    async def on_message(message):
        # 봇 자신의 메시지이거나 다른 봇의 메시지는 무시
        if message.author.bot:
            return

        # 봇이 멘션되었거나, 봇에게 온 DM인 경우 반응
        if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            clean_text = message.content.replace(f"<@{client.user.id}>", "").strip()
            if not clean_text:
                return

            async with message.channel.typing():
                try:
                    response = claude.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1500,
                        system=config["role"],
                        messages=[{"role": "user", "content": clean_text}]
                    )
                    reply_text = response.content[0].text
                    # 디스코드 메시지 2000자 제한 분할 전송
                    for chunk in [reply_text[i:i+1900] for i in range(0, len(reply_text), 1900)]:
                        await message.reply(chunk)
                except Exception as e:
                    await message.reply(f"⚠️ 오류가 발생했습니다: {str(e)}")

    return client, os.environ.get(config["env"])

async def main():
    clients = []
    for cfg in BOT_CONFIGS:
        token = os.environ.get(cfg["env"])
        if token:
            c, t = make_client(cfg)
            clients.append(c.start(t))
        else:
            print(f"경고: {cfg['env']} 토큰이 설정되지 않아 해당 봇을 건너뜁니다.")

    if clients:
        await asyncio.gather(*clients)
    else:
        print("실행할 수 있는 봇 토큰이 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
