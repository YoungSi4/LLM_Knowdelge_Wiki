# Unity ECS: Entity Command Buffer (ECB) 개요

## 1. ECB란 무엇인가?
Entity Command Buffer(ECB)는 Unity ECS 환경에서 **구조적 변경(Structural Changes)**을 안전하게 수행하기 위해 사용하는 명령 기록(Recording) 시스템입니다. 

* **구조적 변경이란?** 엔티티 생성(Create), 파괴(Destroy), 컴포넌트 추가(Add) 및 제거(Remove) 등 메모리 청크(Chunk)의 재배치를 유발하는 작업입니다.
* 멀티스레드 환경(Job System) 내부에서는 데이터 레이아웃이 실시간으로 바뀌면 데이터 경합(Race Condition)이나 유효하지 않은 메모리 참조가 발생할 수 있기 때문에 구조적 변경이 **엄격히 금지**되어 있습니다.

## 2. ECB의 동작 방식
ECB는 구조적 변경을 즉시 실행하지 않고, 일종의 '대기열(Queue)'에 명령을 기록해 두었다가 나중에 한 번에 일괄 처리합니다.

1. **기록 (Record):** Job 내부에서 엔티티 생성, 컴포넌트 추가 등의 명령을 ECB에 기록합니다. 이때 실제 데이터는 변경되지 않습니다.
2. **재생 (Playback):** Job 연산이 모두 끝난 후, 메인 스레드(또는 동기화 지점인 Sync Point)에서 ECB에 쌓인 명령들을 순차적으로 실제 메모리에 적용합니다.
3. **폐기 (Dispose):** 사용이 끝난 임시 메모리를 해제합니다. (시스템이 제공하는 `EntityCommandBufferSystem`을 사용하면 자동 관리됨)

## 3. ECB 사용 시점 및 이점
* **Job 내부에서의 생성/파괴:** 시스템 로직(IJobEntity 등) 안에서 총알을 발사하거나(생성), 체력이 0이 된 적을 없앨 때(파괴) 필수적으로 사용됩니다.
* **Sync Point 최소화:** 구조적 변경은 파이프라인의 병목(Stall)을 유발하므로, 수많은 스레드에서 산발적으로 발생하는 변경 요청을 ECB에 모아서 단 한 번의 동기화 지점(Sync Point)에서 일괄 처리(Batch)하여 **최상의 퍼포먼스를 보장**합니다.

## 4. 간단한 사용 예제 (개념적 코드)

```csharp
using Unity.Entities;

public partial struct SpawnSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        // 1. ECB 생성 (시스템 관리를 받는 자동 할당자 사용)
        var ecbSingleton = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>();
        var ecb = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged);

        // 2. Job 스케줄링 (ECB를 Job에 전달)
        new SpawnJob
        {
            ECB = ecb.AsParallelWriter() // 멀티스레드 병렬 기록을 위한 Writer
        }.ScheduleParallel();
    }
}

public partial struct SpawnJob : IJobEntity
{
    public EntityCommandBuffer.ParallelWriter ECB;

    // chunkIndexInQuery를 사용하여 병렬 환경에서 안전하게 정렬 기록
    private void Execute([ChunkIndexInQuery] int sortKey, ref EnemyComponent enemy, Entity entity)
    {
        if (enemy.Health <= 0)
        {
            // 실제 파괴가 아니라 '파괴하겠다'고 ECB에 기록만 수행
            ECB.DestroyEntity(sortKey, entity);
        }
    }
}
```
