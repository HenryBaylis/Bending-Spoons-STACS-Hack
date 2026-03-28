# Report: Neurosurgeon — Collaborative Intelligence Between the Cloud and Mobile Edge

**Authors:** Yiping Kang, Johann Hauswald, Cao Gao, Austin Rovinski, Trevor Mudge, Jason Mars, Lingjia Tang (University of Michigan, Clarity Lab)
**Venue:** ASPLOS '17, Xi'an, China
**DOI:** https://doi.org/10.1145/3037697.3037698

---

## 1. Problem

Intelligent personal assistants (Siri, Google Now, Cortana) rely on Deep Neural Networks (DNNs) and currently follow a **cloud-only** model: the mobile device uploads raw input (image, speech) over the wireless network, and all inference runs on remote servers. This creates two problems:

- **High latency** — data transfer over 3G/LTE dominates end-to-end response time, often accounting for over 94% of total latency.
- **High mobile energy consumption** — wireless transmission is far more energy-expensive than local computation in many cases.

Meanwhile, modern mobile SoCs (e.g., NVIDIA Tegra K1) are increasingly capable, raising the question: should some or all DNN computation be moved to the device?

---

## 2. Key Insight

DNN computation is structured as a sequence of layers. Each layer has different:
- **Computation cost** — how long it takes on mobile vs. cloud.
- **Data size** — how much data it outputs (which must be transferred if the partition point fal]
"ls here).

This means there is an **optimal partition point** — a layer after which the mobile device hands off to the cloud — that minimises latency or energy. This point varies by DNN architecture, wireless network type, mobile hardware, and datacenter load. A static cloud-only or mobile-only policy leaves significant performance on the table.

---

## 3. DNN Layer Analysis

The paper studies 8 DNN benchmarks across computer vision (IMC/AlexNet, VGG, FACE/DeepFace, DIG/MNIST), speech (ASR/Kaldi), and NLP (POS, NER, CHK/SENNA).

**Layer types characterised:**
| Type | Key property |
|---|---|
| Convolution/Local (`conv`) | High compute, large output data at front-end |
| Pooling (`pool`) | Reduces data size by up to 4.7× |
| Fully-connected (`fc`) | Dominant latency at back-end (e.g., `fc6` = 45% of AlexNet time) |
| Activation (`relu`, `sig`, `htanh`) | Lightweight, data size unchanged |
| Normalisation, Softmax, Argmax | Lightweight, data-reducing at end |

**Key observations from AlexNet profiling:**
- Data size is largest at the early convolutional layers and shrinks through pooling layers.
- Fully-connected layers are the most time-consuming on mobile.
- The optimal partition for **latency** is in the middle of the network (between pool5 and fc6 for Wi-Fi/GPU).
- The optimal partition for **energy** is also in the middle (~18% more efficient than cloud-only).

**CV vs. NLP/ASR DNNs differ:** NLP/ASR DNNs consist only of fully-connected and activation layers with nearly constant data sizes, so their best partition points tend to be at the extremities (fully local or fully remote).

---

## 4. The Neurosurgeon System

Neurosurgeon is a lightweight runtime scheduler that automatically partitions DNN execution between mobile and cloud at the layer granularity. It has two phases:

### Deployment Phase
- Profiles the mobile device and cloud server once (not per-application).
- Builds **regression-based performance prediction models** for each layer type, using layer configuration parameters (e.g., filter size/stride for conv layers, neuron count for fc layers) as inputs.
- Models predict per-layer latency and power consumption on both mobile and server.

### Runtime Phase (Algorithm 1)
1. **Analyse** the target DNN — extract each layer's type and configuration.
2. **Predict** latency and energy for each layer on mobile and cloud using stored models.
3. **Evaluate** all candidate partition points, factoring in current wireless bandwidth and datacenter load level.
4. **Select** the partition point that minimises end-to-end latency **or** mobile energy (user-configurable objective).
5. **Execute** the DNN: mobile runs layers up to the partition point, sends the intermediate output to the server, server completes inference and returns the result.

The algorithm is lightweight (simple regression evaluation) and runs entirely on the mobile device with no per-application profiling required.

---

## 5. Implementation

Neurosurgeon is prototyped using modified Caffe instances:
- **NSmobile** — runs on the mobile device (NVIDIA Jetson TK1: quad-core ARM A15 + Kepler GPU, 2 GB RAM).
- **NSserver** — runs on the datacenter (dual Xeon E5-2620, NVIDIA Tesla K40 GPU).
- Communication via **Apache Thrift** RPC.

Evaluated across 8 benchmarks × 3 network types (Wi-Fi, LTE, 3G) × 2 mobile platforms (CPU, GPU) = 48 configurations.

---

## 6. Results

### 6.1 Latency
- Neurosurgeon achieves the optimal partition point in **44/48** configurations.
- Average latency speedup over cloud-only: **3.1× (up to 40.7×)**.
- Latency speedup is highest for CV apps with GPU mobile (e.g., VGG on 3G: ~20×).
- For ASR, Neurosurgeon correctly identifies full server execution as optimal.

### 6.2 Mobile Energy
- Neurosurgeon selects near-optimal energy partition in **44/48** configurations.
- Average mobile energy reduction: **59.5% (up to 94.7%)** over cloud-only.

### 6.3 vs. MAUI (competing offloading framework)
- MAUI is control-centric (offloads functions/methods); Neurosurgeon is data-centric (partitions at layer boundaries).
- MAUI makes incorrect offloading decisions for VGG, FACE, DIG, ASR because layers of the same type can have very different data sizes within one DNN.
- Neurosurgeon outperforms MAUI by up to **32×** and **1.9× on average**.

### 6.4 Network Variation
- When LTE bandwidth drops, Neurosurgeon dynamically shifts more computation to mobile to maintain consistent latency. The status quo approach suffers large latency spikes during low-bandwidth periods.

### 6.5 Server Load Variation
- As datacenter load increases (0% → 90% utilisation), the status quo latency grows from 105ms to 753ms. Neurosurgeon adapts by progressively offloading more computation to mobile, keeping latency below 380ms.

### 6.6 Datacenter Throughput
- By pushing computation to mobile devices, Neurosurgeon reduces server query service time.
- Throughput improvement: **1.04× (Wi-Fi)**, **1.43× (LTE)**, **2.36× (3G)** — larger gains on slower networks where more computation is offloaded to mobile.
- Up to **6.7×** throughput improvement when 100% of clients use GPU-equipped devices on 3G.

---

## 7. Comparison to Related Work

| Property | MAUI | COMET | Odessa | CloneCloud | Neurosurgeon |
|---|---|---|---|---|---|
| No program state transfer needed | | | ✓ | | ✓ |
| Data-centric partitioning | | | | | ✓ |
| Low runtime overhead | ✓ | | ✓ | ✓ | ✓ |
| No app-specific profiling | | ✓ | ✓ | ✓ | ✓ |
| No programmer annotation | | ✓ | ✓ | ✓ | ✓ |
| Server load aware | | | | | ✓ |

Neurosurgeon is unique in being data-centric, application-agnostic, and server-load-aware simultaneously.

---

## 8. Conclusions

The cloud-only paradigm for DNN inference is suboptimal. Key takeaways:

1. **Data transfer is the bottleneck**, not computation, for the status quo.
2. **Layer-granularity partitioning** exploits the varying compute/data profiles of DNN layers to dramatically cut latency and mobile energy.
3. The optimal partition point is **dynamic** — it depends on network conditions, server load, mobile hardware, and DNN architecture. A static strategy cannot capture this.
4. Neurosurgeon's lightweight regression models provide accurate, low-overhead predictions without per-application profiling, making it broadly applicable.
5. The approach benefits **all stakeholders**: users get lower latency, mobile devices use less energy, and datacenters serve more queries.
