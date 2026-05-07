# Copilot Instructions

## Repository context

This repository currently contains a course outline for **Geospatial Python Mastery**. Treat the outline PDF as the source of truth for the project’s scope and terminology.

The course is organized as a progression:

1. Python fundamentals and data handling
2. JSON and file processing
3. GeoPandas, Shapely, PyProj, Fiona, and Rasterio
4. PostgreSQL/PostGIS workflows
5. CityJSON parsing and 3D geospatial data
6. Capstone project work that combines files, Python, and PostGIS

When adding or editing repository content, keep that progression in mind so new material stays aligned with the curriculum.

## Commands

No build, test, or lint commands are defined in the current repository snapshot.

If code or notebooks are added later, document the exact commands alongside the implementation so future sessions can run them directly.

## Key conventions

- Keep geospatial workflows explicit about **CRS/projection handling** and coordinate transforms.
- Prefer **validation, logging, and error handling** in file-processing examples.
- Use **PostGIS SQL** for spatial database examples, especially for joins, buffering, intersection, aggregation, and indexing.
- For CityJSON work, preserve the distinction between **schema structure, semantics, and geometry arrays**.
- Favor deliverables that match the course outline: scripts, notebooks, SQL files, and concise instructional material.

## High-level architecture

The repository is currently documentation-first, not application-first. Future work will likely expand into:

- Python data-processing utilities
- Geospatial analysis notebooks or scripts
- Database setup and analysis SQL for PostgreSQL/PostGIS
- CityJSON parsing and extraction workflows
- Capstone-ready examples that combine file I/O, spatial computation, and database integration

Keep new files and examples consistent with that layered structure.
