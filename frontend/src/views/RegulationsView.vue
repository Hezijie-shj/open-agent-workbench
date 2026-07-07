<template>
  <PageShell compact>
    <section class="module-page module-page-tight">
      <aside class="module-side">
        <span class="eyebrow">Policy Compare</span>
        <h1>制度文档比对</h1>
        <p>对示例制度文本与规则库做结构化差异比对, 输出风险项和匹配证据。</p>
        <button class="accent-button block-button" type="button" :disabled="actionKey === 'upload'" @click="uploadDemo">
          {{ actionKey === "upload" ? "上传中..." : "上传示例文档" }}
        </button>
        <button class="dark-button block-button" type="button" :disabled="actionKey === 'create'" @click="createTask">
          {{ actionKey === "create" ? "创建中..." : "新建比对任务" }}
        </button>
        <div class="side-metrics">
          <div><strong>{{ tasks.length }}</strong><span>任务</span></div>
          <div><strong>{{ completedCount }}</strong><span>已完成</span></div>
          <div><strong>{{ selectedTask?.risk_count || 0 }}</strong><span>当前风险</span></div>
        </div>
      </aside>

      <main class="module-main">
        <div class="module-toolbar">
          <div>
            <h2>比对任务</h2>
            <span>{{ loading ? "正在读取任务..." : "后端任务列表与详情联动" }}</span>
          </div>
        </div>

        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="notice error-notice">{{ error }}</p>

        <div class="data-table-wrap compact-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>任务名称</th>
                <th>标准库</th>
                <th>上传时间</th>
                <th>状态</th>
                <th>风险项</th>
                <th>摘要</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in tasks" :key="task.id" :class="{ selected: selectedTask?.id === task.id }">
                <td><strong>{{ task.name }}</strong></td>
                <td>{{ task.standard }}</td>
                <td>{{ task.uploaded_at }}</td>
                <td><span :class="['status-badge', task.status === '已完成' ? 'status-done' : 'status-running']">{{ task.status }}</span></td>
                <td><strong class="red">{{ task.risk_count }}</strong></td>
                <td>{{ task.summary }}</td>
                <td>
                  <button class="outline-button small" type="button" :disabled="actionKey === `detail-${task.id}`" @click="selectTask(task.id)">
                    {{ actionKey === `detail-${task.id}` ? "读取中" : "查看结果" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <section v-if="selectedTask" class="result-panel">
          <div class="result-head">
            <div>
              <h2>{{ selectedTask.name }}</h2>
              <span>{{ selectedTask.summary }}</span>
            </div>
            <span :class="['status-badge', selectedTask.status === '已完成' ? 'status-done' : 'status-running']">{{ selectedTask.status }}</span>
          </div>
          <div class="process-actions">
            <button class="dark-button small" type="button" :disabled="actionKey === 'workflow'" @click="loadWorkflow">
              {{ actionKey === "workflow" ? "读取中" : "完整比对流程" }}
            </button>
            <button class="outline-button small" type="button" :disabled="actionKey === 'single'" @click="loadSingleCompare">
              {{ actionKey === "single" ? "读取中" : "单文档比对" }}
            </button>
            <button class="outline-button small" type="button" :disabled="actionKey === 'fallback'" @click="loadFallback">
              {{ actionKey === "fallback" ? "读取中" : "文本定位兜底" }}
            </button>
          </div>
          <div class="result-grid">
            <div>
              <h3>文件状态</h3>
              <p v-for="file in selectedTask.files || []" :key="file.name">
                <strong>{{ file.name }}</strong><span>{{ file.role }} · {{ file.status }}</span>
              </p>
            </div>
            <div>
              <h3>高亮命中</h3>
              <p v-for="item in selectedTask.highlights || []" :key="item.text">
                <strong>{{ item.text }}</strong><span>第 {{ item.page }} 页 · 相似度 {{ Math.round(item.similarity * 100) }}%</span>
              </p>
            </div>
            <div>
              <h3>匹配兜底</h3>
              <p v-if="matches?.group_y?.length">
                <strong>{{ matches.group_y[0].target_text }}</strong><span>{{ matches.group_y[0].matched_text }}</span>
              </p>
              <p v-if="matches?.group_r">
                <strong>{{ matches.group_r.target_text }}</strong><span>{{ matches.group_r.matched_text }}</span>
              </p>
            </div>
          </div>
          <div v-if="processResult" class="process-panel">
            <h3>{{ processTitle }}</h3>
            <div class="process-steps">
              <span v-for="step in processResult.workflow || []" :key="step.key">
                <strong>{{ step.name }}</strong>
                <em>{{ step.status }}</em>
              </span>
            </div>
          </div>
        </section>
      </main>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  createRegulationTask,
  getRegulationMatches,
  getRegulationSingleDocumentCompare,
  getRegulationTask,
  getRegulationTasks,
  getRegulationTextMatchFallback,
  getRegulationWorkflow,
  type RegulationTask,
  uploadRegulationDemo
} from "../api";
import PageShell from "../components/PageShell.vue";

const tasks = ref<RegulationTask[]>([]);
const selectedTask = ref<any>();
const matches = ref<any>();
const processResult = ref<any>();
const processTitle = ref("");
const notice = ref("");
const error = ref("");
const loading = ref(false);
const actionKey = ref("");
const completedCount = computed(() => tasks.value.filter((task) => task.status === "已完成").length);

async function loadTasks(message = "") {
  loading.value = true;
  error.value = "";
  try {
    const data = await getRegulationTasks();
    tasks.value = data.items;
    if (message) notice.value = message;
  } catch {
    error.value = "制度任务读取失败, 请确认后端服务可用。";
  } finally {
    loading.value = false;
  }
}

async function selectTask(taskId: number) {
  actionKey.value = `detail-${taskId}`;
  error.value = "";
  try {
    selectedTask.value = await getRegulationTask(taskId);
    matches.value = await getRegulationMatches(taskId);
    processResult.value = undefined;
    notice.value = `已读取 ${selectedTask.value.name} 的比对结果`;
  } catch {
    error.value = "结果详情读取失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadWorkflow() {
  if (!selectedTask.value) return;
  actionKey.value = "workflow";
  try {
    processResult.value = await getRegulationWorkflow(selectedTask.value.id);
    processTitle.value = "完整制度文档比对流程";
    notice.value = `完整流程已完成: 成功 ${processResult.value.success_count}, 失败 ${processResult.value.fail_count}`;
  } catch {
    error.value = "完整比对流程读取失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadSingleCompare() {
  if (!selectedTask.value) return;
  actionKey.value = "single";
  try {
    processResult.value = await getRegulationSingleDocumentCompare(selectedTask.value.id);
    processTitle.value = "单文档比对流程";
    notice.value = `单文档比对完成: ${processResult.value.items?.length || 0} 个差异项`;
  } catch {
    error.value = "单文档比对流程读取失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadFallback() {
  if (!selectedTask.value) return;
  actionKey.value = "fallback";
  try {
    processResult.value = await getRegulationTextMatchFallback(selectedTask.value.id);
    processTitle.value = "文本定位与截断兜底";
    notice.value = processResult.value.group_r?.fallback ? "文本定位兜底已启用并补全跨段落命中" : "文本定位命中正常";
  } catch {
    error.value = "文本定位兜底流程读取失败。";
  } finally {
    actionKey.value = "";
  }
}

async function createTask() {
  actionKey.value = "create";
  try {
    const task = await createRegulationTask();
    await loadTasks("已创建一条本地比对任务");
    await selectTask(task.id);
  } catch {
    error.value = "创建任务失败。";
  } finally {
    actionKey.value = "";
  }
}

async function uploadDemo() {
  actionKey.value = "upload";
  try {
    const task = await uploadRegulationDemo();
    await loadTasks("已上传示例文档并创建比对任务");
    await selectTask(task.id);
  } catch {
    error.value = "上传示例文档失败。";
  } finally {
    actionKey.value = "";
  }
}

onMounted(async () => {
  await loadTasks();
  if (tasks.value[0]) await selectTask(tasks.value[0].id);
});
</script>
