from typing import Iterator

from openai import OpenAI
import textwrap
from db_hj3415 import myredis
from chatgpt_hj3415.message_maker import get_c103_data, get_c104_data, get_c101_chart_data, get_c106_data

def make_inquiry(code:str, last_days:int = 60) -> str:
    name = myredis.C101(code).get_name()
    csv_103 = ""
    for page, records in get_c103_data(code):
        if page.endswith('y'):
            page = page[4:-1] + "(연간)"
        elif page.endswith('q'):
            page = page[4:-1] + "(분기)"
        else:
            page = page[4:-1]
        csv_103 += f"{page} - {records}\n"
    csv_104 = ""
    for page, records in get_c104_data(code):
        if page.endswith('y'):
            page = "투자지표(연간)"
        elif page.endswith('q'):
            page = "투자지표(분기)"
        else:
            page = "투자지표"
        csv_104 += f"{page} - {records}\n"
    csv_106 = ""
    for page, records in get_c106_data(code):
        if page.endswith('y'):
            page = "동종업종비교(연간)"
        elif page.endswith('q'):
            page = "동종업종비교(분기)"
        else:
            page = "동종업종비교"
        csv_106 += f"{page} - {records}\n"
    chart_data = f"직전{last_days}일간 주가 추이: {get_c101_chart_data(code, last_days=last_days)}"

    return (f"{name}({code})의 다음의 데이터(재무분석, 투자지표, 업종비교, 주가)를 이용해서 향후 기업의 상황과 주가 추이에 대해 분석해줘\n"
            f"{csv_103}"
            f"{csv_104}"
            f"{csv_106}"
            f"{chart_data}")


def run(code:str) -> str:
    client = OpenAI()  # 클라이언트 인스턴스 생성

    messages = [
        {"role": "system", "content": "당신은 한국어를 사용하는 금융 애널리스트입니다. 주식에 대해 잘 모르는 고객에게 설명하듯 친절하고 쉽게 안내해 주세요."},
        {"role": "user",
         "content": make_inquiry(code)},
    ]

    full_answer = ""  # 여기에 이어 붙임

    while True:
        resp = client.chat.completions.create(
            model="o3",
            messages=messages,
            max_completion_tokens=3000,  # 충분히 큰 값
            response_format={"type": "text"},  # 텍스트만
        )

        part = resp.choices[0].message.content
        full_answer += part
        print(textwrap.shorten(part, 100))  # (보기용) 100자만 미리 보기

        # 모델이 스스로 끝냈으면 break
        if resp.choices[0].finish_reason != "length":
            break

        # 더 필요하면 “계속”을 붙여서 다시 요청
        messages.append({"role": "assistant", "content": part})
        messages.append({"role": "user", "content": "계속"})  # 한 마디만 추가

    return full_answer

def run_with_progress(code: str) -> Iterator[dict]:
    """진행률·부분 답변을 순차적으로 yield, 마지막엔 전체 답변 돌려줌"""
    client = OpenAI()
    messages = [
        {"role": "system",
         "content": "당신은 한국어를 사용하는 금융 애널리스트입니다. 주식에 대해 잘 모르는 고객에게 설명하듯 친절하고 쉽게 안내해 주세요."},
        {"role": "user", "content": make_inquiry(code)},
    ]

    full_answer, step = "", 0

    yield {
        "report_done": False,
        "progress": 0,
        "status": f"리포트 생성 시작",
        "chunk": "",
    }

    base = 0

    while True:
        resp = client.chat.completions.create(
            model="o3",
            messages=messages,
            max_completion_tokens=3000,
            response_format={"type": "text"},
        )

        part = resp.choices[0].message.content or ""
        full_answer += part
        step += 1

        # 1) 실제 응답 도착 시, 논리적으로 10 % 올린다고 가정
        target = min(base + 10, 90)

        # 2) ★ time.sleep() 없이 가짜 단계만 여러 번 yield
        for p in range(base + 1, target):
            yield {"progress": p, "status": "리포트 생성 중…"}  # 아주 빠르게 여러 번 보내도 OK

        base = target
        yield {"progress": base, "chunk": part, "status": f"{base}% 완료"}

        if resp.choices[0].finish_reason != "length":
            break

        messages.append({"role": "assistant", "content": part})
        messages.append({"role": "user",      "content": "계속"})

    yield {
        "report_done": True,
        "progress": 95,  # 완료 직전에 95%
        "status": "리포트 본문 생성 완료",
        "answer": full_answer,
    }