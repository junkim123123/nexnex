#!/usr/bin/env python3
"""
Sample Analysis CLI - Phase 3: 엔드투엔드 테스트용 스크립트

이 스크립트는 Streamlit 없이 분석 엔진을 테스트하기 위한 CLI 엔트리포인트입니다.

사용법:
    python scripts/run_sample_analysis.py

또는:
    python scripts/run_sample_analysis.py "새우깡 5,000봉지 미국에 4달러에 팔거야"
"""

import sys
import json
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.nlp_parser import parse_user_input
from core.analysis_engine import run_analysis
from core.errors import ParsingError, NexSupplyError


def main():
    """메인 함수: 전체 파이프라인 실행"""
    
    # 샘플 입력 (명령줄 인자가 없으면 기본값 사용)
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = "새우깡 5,000봉지 미국에 4달러에 팔거야"
    
    print("=" * 80)
    print("NexSupply Analysis Engine - CLI Test")
    print("=" * 80)
    print(f"\n📝 입력: {user_input}\n")
    print("-" * 80)
    
    try:
        # Step 1: 자연어 파싱
        print("\n[1/2] 자연어 파싱 중...")
        print("-" * 80)
        spec = parse_user_input(user_input)
        
        print(f"✅ 파싱 완료:")
        print(f"   - 제품: {spec.product_name}")
        print(f"   - 수량: {spec.quantity:,} {spec.unit_type}")
        print(f"   - 경로: {spec.origin_country} → {spec.destination_country}")
        print(f"   - 소매 가격: ${spec.target_retail_price:.2f}" if spec.target_retail_price else "   - 소매 가격: (미지정)")
        print(f"   - 채널: {spec.channel or '(미지정)'}")
        if spec.data_warnings:
            print(f"   ⚠️ 경고: {', '.join(spec.data_warnings)}")
        
        # Step 2: 분석 실행
        print("\n[2/2] 분석 실행 중...")
        print("-" * 80)
        result = run_analysis(spec)
        
        # Step 3: 결과 출력
        print("\n" + "=" * 80)
        print("📊 분석 결과")
        print("=" * 80)
        
        # 비용 시나리오
        cost_scenarios = result.get('cost_scenarios', {})
        print(f"\n💰 비용 시나리오 (per unit):")
        print(f"   - Base: ${cost_scenarios.get('base', 0):.2f}")
        print(f"   - Best: ${cost_scenarios.get('best', 0):.2f}")
        print(f"   - Worst: ${cost_scenarios.get('worst', 0):.2f}")
        
        # 수익성
        profitability = result.get('profitability', {})
        print(f"\n💵 수익성:")
        print(f"   - 소매 가격: ${profitability.get('retail_price', 0):.2f}")
        print(f"   - 랜디드 코스트: ${profitability.get('unit_ddp', 0):.2f}")
        print(f"   - 순이익: ${profitability.get('net_profit_per_unit', 0):.2f}")
        print(f"   - 마진: {profitability.get('net_profit_percent', 0):.1f}%")
        
        # 리스크 스코어
        risk_scores = result.get('risk_scores', {})
        print(f"\n⚠️ 리스크 스코어:")
        print(f"   - 성공 확률: {risk_scores.get('success_probability', 0):.1%}")
        print(f"   - 전체 리스크: {risk_scores.get('overall_risk_score', 0):.1f}/100")
        print(f"   - 가격 리스크: {risk_scores.get('price_risk', 0):.1f}/100")
        print(f"   - 리드타임 리스크: {risk_scores.get('lead_time_risk', 0):.1f}/100")
        print(f"   - 규제 리스크: {risk_scores.get('compliance_risk', 0):.1f}/100")
        print(f"   - 평판 리스크: {risk_scores.get('reputation_risk', 0):.1f}/100")
        
        # 데이터 품질
        data_quality = result.get('data_quality', {})
        print(f"\n📊 데이터 품질:")
        used_fallbacks = data_quality.get('used_fallbacks', [])
        if used_fallbacks:
            print(f"   ⚠️ Fallback 사용: {', '.join(used_fallbacks)}")
        else:
            print(f"   ✅ 모든 데이터가 실제 데이터 소스에서 조회됨")
        print(f"   - 유사 거래 데이터: {data_quality.get('reference_transaction_count', 0)}건")
        
        # 전체 JSON 출력 (디버깅용)
        print("\n" + "=" * 80)
        print("📄 전체 결과 JSON (디버깅용)")
        print("=" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 80)
        print("✅ 분석 완료")
        print("=" * 80)
        
        return 0
        
    except ParsingError as e:
        print(f"\n❌ 파싱 오류: {e}")
        return 1
    except NexSupplyError as e:
        print(f"\n❌ 분석 오류: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

