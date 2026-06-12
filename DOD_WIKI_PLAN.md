# 데이터 지향 설계 (Data-Oriented Design, DOD) 위키 마스터 기획안

이 문서는 게임 개발 및 고성능 소프트웨어 아키텍처에서 핵심적으로 사용되는 **Data-Oriented Design (DOD)** 원칙을 체계적으로 정리하기 위한 위키 구조 기획안입니다. 에이전트(Planner/Writer)는 본 기획안의 구조를 엄격히 준수하여 위키 문서를 작성해야 합니다.

## 1. 지식 체계 (Core Pillars)

### 파트 I: DOD의 의의 및 목표 (Philosophy & Goals)
- **성능의 한계 돌파**: 객체 지향 프로그래밍(OOP)의 구조적 한계와 메모리 병목 현상(Memory Bottleneck) 극복.
- **데이터 중심적 사고**: 추상적인 객체(Object)가 아닌 실제 '데이터의 흐름과 변환(Transformation)'을 중심으로 시스템을 설계.
- **하드웨어 친화적 설계**: 컴파일러와 CPU가 가장 효율적으로 연산할 수 있는 최적의 환경 제공.

### 파트 II: DOD 구조 및 아키텍처 (Architecture)
- **SoA vs AoS**: 구조체의 배열(Array of Structures)과 배열의 구조체(Structure of Arrays) 간 데이터 레이아웃 차이 및 성능 비교.
- **ECS (Entity Component System)**: DOD 철학을 게임 엔진에 구현하기 위한 표준 아키텍처 패턴.
  - **Entity**: 로직이나 데이터를 갖지 않는 순수 식별자 (ID).
  - **Component**: 연속된 메모리 배열(Arrays)로 관리되는 순수한 데이터 뭉치.
  - **System**: 컴포넌트 배열을 순회하며 일괄적(Batch)으로 로직을 처리하는 함수.

### 파트 III: 기반 CS 지식 (Computer Science Foundations)
- **메모리 계층 구조 (Memory Hierarchy)**: 메인 메모리(RAM)와 CPU 고속 캐시(L1, L2, L3) 간의 극단적인 속도 차이.
- **캐시 지역성 (Cache Locality)**: 공간적 지역성(Spatial Locality)과 시간적 지역성(Temporal Locality)의 중요성.
- **캐시 라인과 프리패치 (Cache Lines & Prefetching)**: 데이터 연속성이 CPU의 캐시 적중률(Cache Hit)과 연산 속도를 극대화하는 하드웨어적 원리.

---

## 2. 권장 위키 목차 (Wiki Structure)

### 0. Overview
### [[INDEX]] (통합 인덱스)
### [[DOD_Foundations]] (DOD의 기본 개념과 도입 배경)

## 1. Core Principles
### [[Data_vs_Objects]] (데이터 변환 vs 객체 지향 상태 관리)
### [[Memory_and_Cache_Locality]] (캐시 적중률을 높이는 메모리 설계)
### [[AoS_and_SoA]] (데이터 레이아웃 구조 비교)

## 2. Implementation: ECS (Entity Component System)
### [[ECS_Architecture_Overview]] (ECS 아키텍처 개요 및 작동 방식)
### [[Components_and_Memory_Alignment]] (컴포넌트 설계와 메모리 정렬 기준)
### [[Systems_and_Data_Processing]] (시스템의 순차적 데이터 처리 로직)

## 3. Advanced CS Concepts
### [[CPU_Pipeline_and_Branch_Prediction]] (CPU 파이프라인과 분기 예측 최적화)
### [[Data_Oriented_Multithreading]] (DOD 환경에서의 멀티스레딩 최적화 접근법)

---

## 3. 요약 및 에이전트 지침
- **목표**: DOD의 철학, 아키텍처, 기저에 깔린 하드웨어 CS 지식을 통합하여 완벽한 게임 개발 최적화 레퍼런스 구축.
- **에이전트 작성 원칙**: 
  1. 메인 컨덕터(Planner/Writer)는 제공된 원본(`raw/` 데이터) 내용만을 사용하여 이 기획안의 구조에 맞게 지식을 배치할 것.
  2. 객체 지향(OOP)과의 명확한 비교 대조표(Table)를 포함하여 설명할 것.
  3. ECS 구조와 데이터 흐름은 Mermaid 다이어그램을 적극 활용하여 시각적으로 압축할 것.
