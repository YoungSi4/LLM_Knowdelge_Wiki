# Data-Oriented Design (DOD) in Game Development

Data-Oriented Design (DOD) is a programming paradigm that focuses on how data is laid out in memory and how it is accessed by the CPU, in order to maximize performance. Unlike Object-Oriented Programming (OOP) which organizes code around "objects" and their behavior, DOD organizes code around the data transformations.

## The Memory Bottleneck & Cache Locality
Modern CPUs are incredibly fast at processing instructions, but fetching data from main memory (RAM) is relatively slow. To mitigate this, CPUs use high-speed caches (L1, L2, L3).
- **Cache Lines**: CPUs fetch data from RAM in chunks called cache lines (typically 64 bytes).
- **Cache Misses**: If the CPU needs data that isn't in the cache, a "cache miss" occurs, forcing the CPU to stall for hundreds of cycles while data is fetched from RAM.
- **Cache Locality**: DOD aims to maximize cache hits by storing data that is processed together contiguously in memory. When the CPU fetches one piece of data, the subsequent data is automatically loaded into the cache line.

## OOP vs. DOD
In traditional OOP, game objects (e.g., Enemies) contain all their data (position, health, rendering info). This is known as Array of Structures (AoS).
When iterating through all enemies just to update their positions, the CPU pulls in health and rendering data into the cache as well, wasting precious cache space.

DOD favors **Structure of Arrays (SoA)**. All positions are stored in one array, all health values in another. A system updating positions only loads the highly packed position array, achieving perfect cache locality.

## Entity Component System (ECS)
ECS is the most popular architectural pattern for applying DOD in game development.
1. **Entities**: Simply IDs (like database keys). They don't contain logic or data.
2. **Components**: Pure data structures (e.g., `PositionComponent`, `VelocityComponent`) stored in contiguous arrays.
3. **Systems**: Logic functions that iterate over specific arrays of components. For example, a `MovementSystem` iterates over arrays of `Position` and `Velocity` to update positions.

### Archetypes
Advanced ECS frameworks use "Archetypes" to group entities that have the exact same set of components. This allows systems to iterate through memory completely linearly without skipping elements, fully maximizing CPU prefetching and cache locality.

## Summary
By respecting the hardware and designing around data flow rather than abstract real-world concepts, DOD significantly boosts performance, making it essential for modern, high-performance game engines.
