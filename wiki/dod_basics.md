# 데이터 지향 설계 (Data-Oriented Design, DOD) 위키

## [[INDEX]]
- **[DOD Foundations](#dod-foundations)**: 도입 배경과 철학
- **[Core Principles](#core-principles)**: 데이터 vs 객체, 메모리 설계, 레이아웃 비교
- **[ECS Architecture](#ecs-architecture)**: 시스템 구현 구조
- **[Advanced Concepts](#advanced-concepts)**: 하드웨어 최적화

---

## [[DOD_Foundations]]
DOD는 추상적인 객체 상태 관리가 아닌, 데이터의 흐름과 변환에 집중하여 CPU의 하드웨어 잠재력을 극대화하는 설계 철학입니다.

| 항목 | 객체 지향 프로그래밍 (OOP) | 데이터 지향 설계 (DOD) |
| :--- | :--- | :--- |
| **핵심** | 상태를 가진 객체 (Object) | 데이터 변환 (Transformation) |
| **초점** | 캡슐화, 상속, 다형성 | 메모리 레이아웃, 캐시 최적화 |
| **데이터** | 객체 내부에 분산 저장 | 연속된 배열(Array)에 밀집 저장 |

---

## [[Core_Principles]]

### [[Data_vs_Objects]]
데이터 중심 사고는 CPU가 데이터를 가져오는 효율성을 극대화합니다. OOP가 가상 함수 호출 및 포인터 간접 참조로 인한 캐시 미스(Cache Miss)를 유발한다면, DOD는 데이터를 연속적인 스트림으로 구성하여 처리합니다.

### [[Memory_and_Cache_Locality]]
캐시 지역성을 높이기 위해 데이터 접근 순서와 배치가 필수적입니다.
- **공간적 지역성 (Spatial Locality)**: 배열 요소들이 인접하여 메모리에 위치.
- **시간적 지역성 (Temporal Locality)**: 한 번 사용한 데이터가 짧은 시간 내 재사용.

### [[AoS_and_SoA]]
```mermaid
graph TD
    AoS[AoS: Array of Structures] --> Structure[Struct {x, y, z}]
    SoA[SoA: Structure of Arrays] --> Arrays[Array X, Array Y, Array Z]
    Structure -->|구조체 단위 접근| Memory1[Memory: x,y,z, x,y,z...]
    Arrays -->|데이터 속성별 접근| Memory2[Memory: x,x,x... y,y,y... z,z,z...]
```
- **AoS**: 데이터를 객체 단위로 다루기 유리하나 캐시 효율이 낮음.
- **SoA**: 특정 데이터 속성만 추출하여 병렬 연산(SIMD) 및 캐시 효율 극대화.

---

## [[Implementation: ECS (Entity Component System)]]

### [[ECS_Architecture_Overview]]
```mermaid
graph LR
    Entity[Entity ID] --> Component[Component Data]
    Component --> System[System Logic]
    System -->|Batch Processing| Component
```

### [[Components_and_Memory_Alignment]]
컴포넌트는 식별자 없는 순수 데이터 구조체입니다. 컴포넌트는 메모리 정렬을 통해 캐시 라인(Cache Line)에 최적화되도록 설계됩니다.

### [[Systems_and_Data_Processing]]
시스템은 데이터를 소유하지 않으며, 특정 컴포넌트 조합을 가진 엔티티를 필터링하여 일괄 처리합니다.

---

## [[Advanced_CS_Concepts]]

### [[CPU_Pipeline_and_Branch_Prediction]]
조건 분기(if-else)를 최소화하여 CPU 파이프라인의 분기 예측 실패(Branch Misprediction)를 방지하는 것이 DOD 최적화의 핵심입니다.

### [[Data_Oriented_Multithreading]]
데이터가 독립적인 배열 형태로 존재하므로, 공유 데이터 잠금(Locking) 없이 병렬 처리가 용이합니다. 데이터를 시스템 단위로 분할하여 코어 간 경합을 최소화합니다.