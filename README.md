# Multi-Agent AI System for Educational Process Simulation

## Project Overview

This project focuses on researching and developing a multi-agent AI system that simulates and automates the educational process. The system consists of specialized AI agents that collaborate across different stages of teaching and learning.

## Educational Process Phases

The system is organized into four main phases:

1. **Instructional Design** – Defining learning objectives, curriculum structure, and teaching strategies.
2. **Learning Content Creation** – Generating educational materials, lessons, examples, and exercises.
3. **Teaching Implementation** – Simulating teaching activities and interactions with learners.
4. **Evaluation** – Assessing learning outcomes and providing feedback to improve the educational process.

## Knowledge Graphs and Retrieval-Augmented Generation (RAG)

A key idea of this project is to ground the agents' work in structured knowledge, not only in the language model's internal knowledge. The educational domain is modeled as a **knowledge graph**: nodes are concepts and learning resources, and edges are relationships such as *prerequisite of* or *part of*.

This graph is combined with a **RAG** pipeline:

- **Instructional design agents** use concept dependencies to order the curriculum.
- **Content creation agents** retrieve relevant context before generating lessons and exercises, which reduces hallucinations.
- **Teaching agents** adapt explanations to what the learner already knows.
- **Evaluation agents** link assessment results to graph nodes to find knowledge gaps.

The project also explores whether graph-based retrieval (GraphRAG) gives better educational content than standard vector-based RAG.

## Project Goals

- Explore the application of AI agents in education.
- Design a collaborative multi-agent architecture.
- Investigate communication and coordination between agents.
- Implement a prototype that simulates the educational process.
- Evaluate system performance and opportunities for improvement.
- Model the educational domain as a knowledge graph of concepts, resources, and their relationships
- Integrate a graph-based RAG pipeline to ground agent outputs and evaluate its impact on content quality

## Repository Contents

This repository contains research notes, literature reviews, key concepts, methodology, development progress, and implementation code.

