<template>
  <PageShell compact>
    <section class="module-page">
      <aside class="module-side">
        <RouterLink to="/market" class="back-link compact-link">‹ 智能应用</RouterLink>
        <span class="eyebrow">Document Diff</span>
        <h1>文档差异比对</h1>
        <p>比较标准文档与多个版本文件, 输出条款差异、风险等级和历史记录。</p>
        <button class="accent-button block-button" type="button" :disabled="actionKey === 'create'" @click="createLocalTask">
          {{ actionKey === "create" ? "创建中..." : "新建比对样例" }}
        </button>
        <button class="dark-button block-button" type="button" :disabled="actionKey === 'compare'" @click="compareDocuments">
          {{ actionKey === "compare" ? "提交中..." : "创建比对任务" }}
        </button>
        <div class="side-metrics">
          <div><strong>{{ history.length }}</strong><span>历史任务</span></div>
          <div><strong>{{ completedCount }}</strong><span>已完成</span></div>
          <div><strong>{{ selected?.diffs?.length || 0 }}</strong><span>当前差异</span></div>
        </div>
      </aside>

      <main class="module-main">
        <div class="module-toolbar">
          <div>
            <h2>差异工作台</h2>
            <span>{{ loading ? "正在读取历史..." : selected?.title || "选择左侧任务查看差异" }}</span>
          </div>
        </div>

        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="notice error-notice">{{ error }}</p>
        <div v-if="selected" class="process-actions">
          <button class="dark-button small" type="button" :disabled="actionKey === 'status'" @click="loadStatus">
            {{ actionKey === "status" ? "同步中" : "轮询状态" }}
          </button>
          <button class="outline-button small" type="button" :disabled="actionKey === 'preview'" @click="loadPreview">
            {{ actionKey === "preview" ? "生成中" : "预览链接" }}
          </button>
          <button class="outline-button small" type="button" :disabled="actionKey === 'line-diff'" @click="loadLineDiff">
            {{ actionKey === "line-diff" ? "计算中" : "行级 diff" }}
          </button>
        </div>
        <div v-if="processResult" class="process-panel">
          <h3>{{ processTitle }}</h3>
          <p v-if="processResult.preview_url">{{ processResult.preview_url }}</p>
          <div class="process-steps">
            <span v-for="step in processResult.workflow || []" :key="step.key">
              <strong>{{ step.name }}</strong>
              <em>{{ step.status }}</em>
            </span>
          </div>
        </div>

        <section class="diff-layout refined-diff">
          <aside class="diff-history">
            <button
              v-for="item in history"
              :key="item.task_id"
              :class="{ active: selected?.task_id === item.task_id }"
              type="button"
              :disabled="actionKey === item.task_id"
              @click="selectTask(item.task_id)"
            >
              <strong>{{ item.title }}</strong>
              <span>{{ item.status }} · {{ item.created_at }}</span>
            </button>
          </aside>
          <main class="diff-detail" v-if="selected">
            <div class="diff-files">
              <div><span>标准文档</span><strong>{{ selected.origin_file }}</strong></div>
              <div><span>比对文档</span><strong>{{ selected.compare_files?.join(" / ") }}</strong></div>
            </div>
            <table class="data-table">
              <thead><tr><th>条款</th><th>原文</th><th>差异文本</th><th>等级</th></tr></thead>
              <tbody>
                <tr v-for="diff in selected.diffs" :key="diff.clause">
                  <td><strong>{{ diff.clause }}</strong></td>
                  <td>{{ diff.before }}</td>
                  <td>{{ diff.after }}</td>
                  <td><span :class="['status-badge', diff.level === 'high' ? 'status-risk' : 'status-running']">{{ diff.level }}</span></td>
                </tr>
              </tbody>
            </table>
          </main>
        </section>
      </main>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  compareDocumentDiffDemo,
  createDocumentDiffDemo,
  getDocumentDiffDetail,
  getDocumentDiffHistory,
  getDocumentDiffLocalLineDiff,
  getDocumentDiffPreview,
  getDocumentDiffStatus
} from "../api";
import PageShell from "../components/PageShell.vue";

const history = ref<any[]>([]);
const selected = ref<any>();
const notice = ref("");
const error = ref("");
const loading = ref(false);
const actionKey = ref("");
const processResult = ref<any>();
const processTitle = ref("");
const completedCount = computed(() => history.value.filter((item) => item.status === "completed").length);

async function loadHistory(message = "") {
  loading.value = true;
  error.value = "";
  try {
    const data = await getDocumentDiffHistory();
    history.value = data.items;
    if (message) notice.value = message;
  } catch {
    error.value = "文档差异历史读取失败, 请确认后端服务可用。";
  } finally {
    loading.value = false;
  }
}

async function selectTask(taskId: string) {
  actionKey.value = taskId;
  error.value = "";
  try {
    selected.value = await getDocumentDiffDetail(taskId);
    processResult.value = undefined;
    notice.value = `已加载 ${selected.value.title}`;
  } catch {
    error.value = "文档差异详情读取失败。";
  } finally {
    actionKey.value = "";
  }
}

async function createLocalTask() {
  actionKey.value = "create";
  try {
    const detail = await createDocumentDiffDemo();
    await loadHistory("已创建本地比对样例");
    selected.value = detail;
  } catch {
    error.value = "创建文档差异样例失败。";
  } finally {
    actionKey.value = "";
  }
}

async function compareDocuments() {
  actionKey.value = "compare";
  try {
    const result = await compareDocumentDiffDemo();
    await loadHistory("已创建文档差异比对任务");
    processResult.value = result;
    processTitle.value = "创建文档差异比对任务";
    selected.value = await getDocumentDiffDetail(result.task_id);
  } catch {
    error.value = "创建文档差异比对任务失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadStatus() {
  if (!selected.value?.task_id) return;
  actionKey.value = "status";
  try {
    const result = await getDocumentDiffStatus(selected.value.task_id);
    processResult.value = result;
    processTitle.value = "任务状态轮询";
    if (result.detail) selected.value = result.detail;
    await loadHistory();
    notice.value = `任务状态: ${result.status}`;
  } catch {
    error.value = "任务状态同步失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadPreview() {
  if (!selected.value?.task_id) return;
  actionKey.value = "preview";
  try {
    processResult.value = await getDocumentDiffPreview(selected.value.task_id);
    processTitle.value = "文档预览授权";
    notice.value = "已生成本地预览链接";
  } catch {
    error.value = "预览链接生成失败。";
  } finally {
    actionKey.value = "";
  }
}

async function loadLineDiff() {
  if (!selected.value?.task_id) return;
  actionKey.value = "line-diff";
  try {
    processResult.value = await getDocumentDiffLocalLineDiff(selected.value.task_id);
    processTitle.value = `本地行级 diff, 相似度 ${Math.round(processResult.value.similarity * 100)}%`;
    notice.value = `行级 diff 完成: +${processResult.value.added_lines} / -${processResult.value.deleted_lines}`;
  } catch {
    error.value = "行级 diff 计算失败。";
  } finally {
    actionKey.value = "";
  }
}

onMounted(async () => {
  await loadHistory();
  if (history.value[0]) await selectTask(history.value[0].task_id);
});
</script>
