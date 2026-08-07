# 4 Process DOE Summary

이 문서는 AI DOE Planner 프로젝트에서 다룰 수 있는 4가지 공정의 DOE 관점을 정리한다.

대상 공정:

1. Wafer Sawing
2. Die Attach
3. Wire Bonding
4. Molding

핵심 기준은 단순히 "어떤 인자가 중요한가"가 아니라, 실제 프로젝트에서 측정 가능한 Y가 무엇인지, 어떤 X를 안전하게 바꿀 수 있는지, 그리고 1차 DOE 이후 어떤 기준으로 다음 DOE를 선택할지이다.

## 전체 결론

| 공정 | 프로젝트 적합도 | 이유 |
| --- | --- | --- |
| Wire Bonding | 높음 | Pull force, failure code, ball shear처럼 측정/판정 가능한 Y가 비교적 명확하다. 2nd bond 중심 DOE를 만들기 좋다. |
| Die Attach | 높음 | BLT와 die shear를 측정할 수 있으면 매우 좋다. 단, void/bleed가 정량화되지 않으면 guardrail로 두는 것이 현실적이다. |
| Wafer Sawing | 높음 | 실습 전사본과 사진 정리 기준으로 chipping size를 현미경/이미지 툴로 수치화할 수 있다. 5 um 또는 10 um 같은 spec을 먼저 정하고 max chipping, spread, pass/fail로 분석하면 DOE 구조가 명확하다. |
| Molding | 중간 | Wire sweep, void를 수치화할 수 있으면 좋지만, 실습 환경에서는 판정형/등급형 Y가 될 가능성이 크다. 측정 가능성이 가장 큰 변수다. |

현실적인 우선순위는 다음과 같다.

1. Wire Bonding: 2nd bond 중심으로 pull force와 failure code를 본다.
2. Wafer Sawing: chipping size를 직접 측정할 수 있어 feed speed 최적화 스토리가 좋다.
3. Die Attach: BLT와 die shear가 가능하면 품질-양산 trade-off를 보여주기 좋다.
4. Molding: wire sweep/void 측정 방법이 확보될 때 DOE 대상으로 잡는 것이 좋다.

## 1. Wafer Sawing

### DOE 목적

Wafer sawing에서는 절단 품질을 먼저 만족시키고, 남는 품질 마진으로 feed speed를 올려 생산성을 개선하는 것이 핵심이다.

즉, 목표는 다음 순서다.

1. Chipping이 spec 안에 들어오는 조건을 찾는다.
2. Chipping margin이 충분하면 feed speed를 높인다.
3. 품질 악화가 시작되는 경계를 확인한다.

실습 전사본 기준으로 wafer sawing의 주요 Y는 단순한 불량 개수가 아니라 **chipping size**로 잡는 것이 맞다.

강의/실습에서 나온 핵심 근거:

- 불량 개수보다 chipping size를 봐야 한다는 취지의 설명이 있었다.
- chipping 기준은 먼저 정해야 하며, 예시로 5 um 또는 10 um 기준이 언급되었다.
- feed speed가 빨라지면 평균만이 아니라 sigma/spread가 커질 수 있으므로 max, range, stdev를 같이 봐야 한다.
- 측정 위치는 5-point 또는 9-point처럼 미리 정하고, 사진으로 측정 위치를 남기는 방식이 언급되었다.
- 현업에서는 전체를 보고 가장 큰 damage를 중시하지만, 프로젝트에서는 fixed point 측정과 worst observed chipping을 같이 쓰는 방식이 현실적이다.

### 주요 X 후보

| 우선순위 | X | DOE 의미 |
| --- | --- | --- |
| 1 | Feed speed / cutting speed | 품질과 생산성을 동시에 흔드는 핵심 인자 |
| 2 | Spindle RPM | blade 절삭 메커니즘과 chipping에 영향 |
| 3 | Blade type/spec | blade 교체가 가능할 때만 포함 |
| 4 | Cut depth / blade height | UV tape, DAF 조건에 따라 중요하지만 1차 DOE에서는 고정 가능 |
| 5 | DI water flow | 보통 고정/모니터링 |
| 6 | Tape/UV condition | 고정 조건 또는 block 조건 |

### 주요 Y 후보

| Y | 타입 | 사용 방식 |
| --- | --- | --- |
| Maximum chipping size | 연속형 | 1순위 품질 Y. 낮을수록 좋다. |
| Chipping pass/fail | 이진형 | 5 um 또는 10 um 등 사전 정의한 spec 만족 여부. baseline 선정에 중요하다. |
| Chipping range/stdev | 연속형 | 반복 안정성 확인용 |
| Mean chipping size | 연속형 | 보조 품질 지표 |
| Cutting time / throughput | 연속형 | 품질 만족 이후 양산성 Y |
| Blade break, chip fly-off | guardrail | 발생 시 조건 탈락 또는 별도 원인 조사 |

권장 측정 세트:

| 항목 | 권장 방식 |
| --- | --- |
| Primary Y | Maximum chipping size |
| Support Y | Mean chipping size, range, stdev |
| Spec Y | Chipping pass/fail by 5 um 또는 10 um 기준 |
| 위치 기준 | 5-point 또는 9-point 고정 위치 |
| Guardrail | 측정 위치 외 가장 큰 visible chipping |
| 증거 | 측정 위치 사진 저장 |

### 1차 DOE 추천

측정 시간이 제한되면 4인자 screening보다 2~3인자 중심 DOE가 더 현실적이다.

| 상황 | 추천 DOE |
| --- | --- |
| 시간이 매우 짧음 | Feed speed × spindle RPM, 2인자 2수준 완전요인 |
| blade 교체 가능 | Feed speed × spindle RPM × blade type, 3인자 2수준 완전요인 |
| 인자 불확실성이 큼 | 4인자 8-run 부분요인 가능하지만, 교락 구조를 명확히 기록 |

### 다음 DOE 판단

| 1차 결과 | 다음 방향 |
| --- | --- |
| 대부분 chipping fail | feed speed를 낮추거나 spindle/blade 조건을 재설정하는 rescue DOE |
| pass는 있지만 margin이 작음 | 반복 확인 + 좁은 범위 안정화 DOE |
| pass margin이 충분함 | feed speed를 올리는 productivity improvement DOE |
| 특정 조합에서만 fail | feed speed × spindle RPM 또는 blade × feed interaction 확인 |

## 2. Die Attach

### DOE 목적

Die attach에서는 접착 강도와 BLT를 동시에 만족시키는 baseline을 찾고, 이후 epoxy 사용량과 공정 시간을 줄일 수 있는지 확인하는 것이 현실적이다.

중요한 점:

- BLT는 spec 범위 안에서 얇을수록 좋다.
- Die shear strength는 하한 spec을 만족해야 한다.
- Epoxy bleed, void는 정량화가 어렵다면 guardrail로 둔다.
- Epoxy amount는 품질 X이면서 동시에 원자재 사용량 관점의 양산성 지표다.

### 주요 X 후보

| 우선순위 | X | DOE 의미 |
| --- | --- | --- |
| 1 | Epoxy dispense amount | BLT, shear, bleed, void에 직접 영향 |
| 2 | Bond force | epoxy spread/contact/BLT에 직접 영향 |
| 3 | Bond time | wetting/contact 안정화, cycle time과 trade-off |
| 4 | Wait/wetting time | epoxy settling, void, cycle time 영향 |
| 보류 | Bond level / overtravel | 장비 설정 의미를 명확히 확인해야 함 |
| 보류 | Cure condition | 별도 공정이면 1차 DOE에서 고정 |

### 주요 Y 후보

| Y | 타입 | 사용 방식 |
| --- | --- | --- |
| Die shear strength | 연속형 | 주요 품질 Y. 하한 spec 만족 필요 |
| BLT | 연속형 | 주요 품질 Y. spec 범위 내에서 낮을수록 선호 |
| Epoxy bleed / contamination | 등급형/이진형 | guardrail |
| Void | 연속형/등급형/이진형 | 정량 가능하면 주요 Y, 아니면 guardrail |
| Process time | 연속형 | secondary production Y |
| Epoxy usage | 연속형 | secondary production Y. 단, 초기 품질 DOE를 압도하지 않게 주의 |

### 중요한 공정 메커니즘

| 관계 | 의미 |
| --- | --- |
| Epoxy amount × bond force | BLT와 epoxy spread를 결정하는 핵심 interaction |
| Epoxy amount 증가 | BLT 증가, shear 개선 가능, bleed risk 증가 |
| Bond force 증가 | BLT 감소, contact 개선 가능, squeeze-out/damage risk 증가 |
| Bond time 증가 | wetting 안정화 가능, cycle time 증가 |
| Epoxy aging/lot | DOE 인자가 아닌데 결과를 지배할 수 있는 hidden confound |

### 1차 DOE 추천

| 상황 | 추천 DOE |
| --- | --- |
| 핵심 인자 3개가 명확함 | Epoxy amount × bond force × bond time, 2수준 완전요인 |
| 4개 인자를 넓게 보고 싶음 | 4인자 8-run 부분요인. 단, epoxy amount × bond force 교락을 피하도록 설계 |
| 실험 수가 매우 적음 | epoxy amount × bond force 중심의 작은 탐색 DOE |

### 다음 DOE 판단

| 결과 | 다음 방향 |
| --- | --- |
| Die shear fail | epoxy amount, bond force, bond time 중 shear를 올릴 수 있는 방향으로 rescue DOE |
| BLT spec out | epoxy amount × bond force 중심으로 BLT 조정 DOE |
| 품질 pass, margin 작음 | confirmation DOE 또는 좁은 범위 안정화 |
| 품질 pass, margin 충분함 | epoxy 절감 또는 time 절감 DOE |
| epoxy 절감 시 shear margin 급감 | 더 줄이지 않고 보수 baseline 선택 |

## 3. Wire Bonding

### DOE 목적

Wire bonding은 2nd bond 쪽을 중심으로 pull force를 spec 이상으로 확보하고, failure code가 위험한 쪽으로 가지 않는 조건을 찾는 것이 핵심이다.

프로젝트 기본 방향:

- 2nd bond 중심으로 본다.
- Pull test force를 주요 Y로 둔다.
- Failure code는 품질 해석과 guardrail로 같이 본다.
- Ball shear는 1st bond가 정상이라는 것을 확인하는 보조/guardrail Y로 둔다.

### 주요 X 후보

| 우선순위 | X | DOE 의미 |
| --- | --- | --- |
| 1 | 2nd US Power | ultrasonic energy의 핵심 |
| 2 | 2nd Bond Force | stitch 접촉/변형/접합 안정성 |
| 3 | 2nd US Time | ultrasonic dose를 결정 |
| 4 | 2nd Force Time | force 유지/접촉 안정성 |
| 고정 | 1st bond parameters | 2nd bond DOE에서는 고정/모니터링 |
| 고정/기록 | capillary, wire, substrate, stage temp | 변동 시 결과 해석이 흐려짐 |

### 주요 Y 후보

| Y | 타입 | 사용 방식 |
| --- | --- | --- |
| Pull force | 연속형 | 주요 Y. 하한 spec 이상 필요 |
| Pull pass/fail | 이진형 | spec 기준 pass 수 |
| Failure code | 범주형 | 위험 failure mode 확인 |
| Ball shear force | 연속형 | 1st bond guardrail |
| Ball shear case | 범주형 | 1st bond 이상 여부 확인 |

### Failure code 해석

| Code | 해석 |
| --- | --- |
| 1~3 | pull force가 충분하면 대체로 허용 가능 또는 관찰 |
| 4~7 | 위험 code. pull force가 높아도 baseline 확정 전에는 위험 후보로 둔다. |

기본 규칙:

- Pull force가 spec 미만이면 탈락.
- Pull force가 spec 이상이어도 code 4~7이 반복되면 baseline으로 바로 채택하지 않는다.
- Code 4~7이 1회성이고 force margin이 충분하면 "위험 후보"로 남기고 확인 DOE를 요구한다.

### 중요한 공정 메커니즘

| 관계 | 의미 |
| --- | --- |
| US Power × US Time | 총 ultrasonic dose |
| US Power × Bond Force | 에너지 전달과 접촉 변형 coupling |
| Bond Force × Force Time | mechanical contact/hold 안정성 |
| 과도한 energy/force | pull force는 오를 수 있지만 pad damage, lift, brittle failure risk 증가 |
| 낮은 energy/force | stitch 접합 부족, wedge failure risk 증가 |

### 1차 DOE 추천

| 상황 | 추천 DOE |
| --- | --- |
| 4인자를 넓게 screening | 4인자 2수준 8-run 부분요인 |
| 실험 시간이 적음 | US power × force × US time, 3인자 2수준 완전요인 |
| failure code가 병목 | force/time/power 조합을 좁혀 guardrail 안정화 DOE |

4인자 8-run을 할 때는 generator를 그냥 고르는 것이 아니라, 중요한 interaction이 주효과와 심하게 섞이지 않도록 설계해야 한다.

우선 보호할 interaction:

1. US Power × US Time
2. US Power × Bond Force
3. Bond Force × Force Time

### 다음 DOE 판단

| 결과 | 다음 방향 |
| --- | --- |
| pull force fail 많음 | energy/contact dose를 올리는 rescue DOE |
| pull force pass지만 code 4~7 발생 | failure mode 안정화 DOE |
| pull force margin 충분, code 안정 | force/time/energy 절감 DOE |
| ball shear guardrail fail | 1st bond 쪽 이상. 2nd bond DOE 결론 보류 |
| 특정 factor 기여율 높지만 병목 Y 개선과 무관 | 병목 Y에 직접 영향을 주는 인자 중심으로 재설계 |

## 4. Molding

### DOE 목적

Molding에서는 wire sweep과 void를 줄이면서, injection time/cycle time을 가능한 낮추는 것이 핵심이다.

단, 실제 프로젝트에서는 wire sweep만 측정 가능할 수도 있다. 이 경우 void는 주요 Y가 아니라 guardrail 또는 가상 검증용 Y로 둔다.

### 주요 X 후보

| 우선순위 | X | DOE 의미 |
| --- | --- | --- |
| 1 | Transfer down slow / transfer speed | flow front, wire sweep, void, injection time에 영향 |
| 2 | Mold temperature | EMC viscosity, flow, cure behavior에 영향 |
| 3 | Transfer pressure | filling, void, flash/overflow에 영향 |
| 4 | Wire loop height | recipe knob라기보다 upstream stress/block factor |
| 고정 | Cure time | 1차 DOE에서는 보통 고정. cure/reliability Y가 있으면 별도 DOE |
| 고정/기록 | EMC lot/storage, preheat, vent, mold cleaning | 결과를 흐릴 수 있는 hidden factor |

### 주요 Y 후보

| Y | 타입 | 사용 방식 |
| --- | --- | --- |
| Wire sweep | 연속형/등급형/이진형 | 주요 Y. 실제 측정 가능성이 가장 중요 |
| Void | count/비율/등급형/이진형 | 가능하면 주요 Y, 아니면 guardrail |
| Short shot / incomplete fill | 이진형/count | guardrail |
| Flash / overflow | 이진형/count | guardrail |
| Warpage/dimension | 연속형 | 측정 가능하면 보조 품질 Y |
| Injection time | 연속형 | secondary production Y |

### 중요한 공정 메커니즘

| 관계 | 의미 |
| --- | --- |
| Transfer speed 증가 | injection time 감소 가능, 하지만 wire sweep/void/flow defect risk 증가 |
| Mold temperature 증가 | viscosity 감소로 fill 개선 가능, cure/void/warpage와 trade-off 가능 |
| Transfer pressure 증가 | fill 개선 가능, flash/overflow/wire stress risk 증가 |
| Wire loop height 낮음 | wire sweep margin 감소 가능. recipe 인자보다 stress condition에 가깝다. |

### 1차 DOE 추천

Molding은 4인자를 무조건 넣기보다 측정 가능한 Y를 먼저 확정해야 한다.

| 상황 | 추천 DOE |
| --- | --- |
| wire sweep과 void 모두 측정 가능 | transfer down slow × mold temp × transfer pressure, 3인자 2수준 완전요인 |
| wire sweep만 측정 가능 | transfer down slow × pressure 중심, mold temp는 가능하면 포함 |
| 가상 검증 또는 충분한 run 가능 | wire loop height를 stress/block factor로 포함한 4인자 DOE |
| 실제 run이 매우 적음 | transfer down slow 중심으로 품질-시간 경계 확인 |

### 다음 DOE 판단

| 결과 | 다음 방향 |
| --- | --- |
| wire sweep fail | transfer speed/pressure/loop height 조건을 보수화하는 rescue DOE |
| void fail | mold temp/pressure/speed 조합 재검토 |
| 품질 pass, injection time 길다 | transfer speed를 높이는 production DOE |
| 품질 pass margin 작다 | confirmation 또는 안정화 DOE |
| 품질 pass margin 충분 | speed/time 개선 DOE |

## 4공정 공통 DOE 엔진 기준

### 1. 먼저 Y 타입을 정한다

| Y 타입 | 분석 방식 |
| --- | --- |
| 연속형 | 효과분석, ANOVA, 회귀분석, 반복 안정성, 예측식 |
| 이진형 pass/fail | pass rate, fail 조건 패턴, 로지스틱 관점, 조건별 위험도 |
| count형 | count/rate 비교, Poisson 또는 rate 기반 해석, 불량 개수 경향 |
| 등급형/범주형 | 코드 분포, 위험 code 빈도, ordinal risk 해석 |
| 보조 생산 Y | 품질 pass 이후에 개선 목표로 사용 |

### 2. 1차 DOE는 "많이 넣기"보다 "측정 가능한 Y에 맞게" 설계한다

이 프로젝트의 실제 실습 DOE는 7시간 안에 진행된다는 제약을 기본값으로 둔다.
장비 세팅, 조건 변경, 측정, 기록, 실수 수정, 결과 리뷰까지 모두 포함하면
순수 실험 run에 쓸 수 있는 시간은 7시간보다 훨씬 짧다.

| 상황 | 추천 |
| --- | --- |
| 엔지니어가 핵심 인자 2~3개를 알고 있음 | 바로 2~3인자 완전요인 DOE |
| 후보 인자가 넓고 불확실함 | 4인자 8-run 부분요인 DOE |
| 교호작용이 매우 중요함 | 4인자 부분요인보다 핵심 2~3인자 완전요인을 우선 검토 |
| 실험 수가 매우 적음 | 통계적 유의성보다 baseline 탐색과 guardrail 확인에 집중 |
| 7시간 실습에서 장비/측정이 익숙하지 않음 | 2인자 DOE + baseline/center/repeat buffer를 우선 검토 |

7시간 제약에서는 "더 많은 factor"보다 "완료 가능한 DOE"가 우선이다.
실행이 어설프면 4인자 screening보다 2인자 full factorial이 더 좋은 evidence를
줄 수 있다.

### 3. Low/High는 장비 한계값이 아니다

Low/High는 장비의 물리적 minimum/maximum이 아니라, 엔지니어가 안전하다고 보는 1차 DOE용 실험 범위다.

따라서 DOE 설계 전에 반드시 구분해야 한다.

| 구분 | 의미 |
| --- | --- |
| 장비 가능 범위 | 장비가 입력 가능한 전체 범위 |
| 공정 안전 범위 | damage나 불량을 과도하게 만들지 않는 범위 |
| 1차 DOE 범위 | 실험 목적상 비교하려는 low/high |
| 2차 DOE 범위 | 1차 결과를 바탕으로 좁히거나 이동한 범위 |

### 4. 다음 DOE는 "가장 큰 기여율"만 보고 정하지 않는다

다음 DOE는 다음 순서로 정한다.

1. 어떤 Y가 병목인지 확인한다.
2. 그 병목 Y를 개선할 수 있는 X가 무엇인지 본다.
3. 그 X가 다른 Y를 악화시키는 trade-off를 확인한다.
4. 품질 spec을 만족하지 못하면 품질 rescue가 우선이다.
5. 품질 spec을 만족하고 margin이 있으면 양산성 개선으로 이동한다.

예를 들어 어떤 인자의 전체 기여율이 커도, 현재 fail을 만드는 병목 Y를 개선하지 못하면 다음 DOE의 중심 인자가 아닐 수 있다.

### 5. Baseline 이후 DOE 방향

| Baseline 상태 | 다음 DOE |
| --- | --- |
| 품질 spec 미만 | rescue DOE |
| 품질 pass지만 margin 작음 | confirmation / robustness DOE |
| 품질 pass, margin 충분 | production improvement DOE |
| 품질 pass, margin 매우 충분 | material/time 절감 DOE |
| 품질과 생산성 trade-off 큼 | mixed confirmation DOE |

### 6. 보고서에 반드시 보여줄 근거

각 DOE cycle마다 다음을 보여줘야 한다.

1. 이 Y가 어떤 타입인지
2. 그래서 어떤 통계 분석을 했는지
3. factor별 효과, 기여율, 방향성
4. 반복 안정성: 평균뿐 아니라 min/max/range
5. pass/fail 또는 failure code 분포
6. 공정 메커니즘상 납득되는지
7. 양산 관점의 이득과 리스크
8. 그래서 왜 다음 DOE mode를 선택했는지
9. 다음 DOE에서 어떤 인자를 고정/변경/제거했는지
10. 그 수준값을 어떤 근거로 잡았는지

## 최종 프로젝트 관점 추천

실제 프로젝트에서 가장 중요한 것은 "멋진 DOE 형태"보다 "측정 가능한 Y와 설득 가능한 다음 DOE 근거"다.

따라서 4공정 중 하나를 고를 때는 다음 질문으로 결정한다.

1. 이 공정에서 주요 Y를 수치화할 수 있는가?
2. spec 또는 pass/fail 기준을 받을 수 있는가?
3. 조절 가능한 X의 low/high를 엔지니어에게 받을 수 있는가?
4. 7시간 안에 세팅, run, 측정, 기록, 리뷰까지 끝낼 수 있는가?
5. 최소 8-run 또는 2인자 완전요인 + baseline/repeat buffer를 돌릴 시간이 있는가?
6. 결과를 보고 다음 DOE 방향을 정리할 시간이 남는가?

이 기준으로 보면 현재 가장 강한 후보는 Wire Bonding과 Die Attach다.

Wafer Sawing은 chipping 측정 기준만 확보하면 매우 좋은 후보가 된다.

Molding은 transfer molding 메커니즘은 좋지만, wire sweep/void 측정이 실제로 가능한지에 따라 DOE 품질이 크게 달라진다.
