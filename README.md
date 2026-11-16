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

A key idea of this project is to ground the agents' work in structured knowledge rather than relying only on the internal knowledge of the language model. The educational domain (topics, concepts, learning objectives, prerequisites, and learning materials) is modeled as a **knowledge graph**, where nodes represent concepts and resources, and edges capture relationships such as *prerequisite of*, *part of*, *related to*, and *assessed by*.

This graph is combined with a **Retrieval-Augmented Generation (RAG)** pipeline:

- **Instructional design agents** traverse the graph to build a logical curriculum order based on concept dependencies.
- **Content creation agents** retrieve relevant documents and graph context before generating lessons, examples, and exercises, which reduces hallucinations and keeps content consistent.
- **Teaching agents** use the graph to adapt explanations to what the learner already knows.
- **Evaluation agents** map assessment results back to graph nodes to identify knowledge gaps and suggest which concepts to revisit.

The goal is to explore how graph-based retrieval (GraphRAG) can improve the accuracy, coherence, and personalization of AI-generated educational content compared to standard vector-based RAG.

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

