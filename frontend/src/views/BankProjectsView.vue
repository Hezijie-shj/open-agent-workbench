<template>
  <PageShell :header="false" compact>
    <section class="module-page">
      <aside class="module-side">
        <RouterLink to="/market" class="back-link compact-link">‹ 智能应用</RouterLink>
        <span class="eyebrow">Statement Lab</span>
        <h1>流水解析任务</h1>
        <p>上传样例、执行单页识别、复核结构化结果并生成报告。</p>
        <button class="accent-button block-button" type="button" :disabled="loading || actionKey === 'create'" @click="addDemoProject">
          {{ actionKey === "create" ? "上传中..." : "上传示例文件" }}
        </button>

        <div class="side-metrics">
          <div><strong>{{ projects.length }}</strong><span>全部任务</span></div>
          <div><strong>{{ doneCount }}</strong><span>已完成</span></div>
          <div><strong>{{ pendingCount }}</strong><span>处理中</span></div>
        </div>
      </aside>

      <main class="module-main">
        <div class="module-toolbar">
          <div>
            <h2>任务队列</h2>
            <span>{{ loading ? "正在读取后端任务..." : `共 ${filteredProjects.length} 条匹配结果` }}</span>
          </div>
          <div class="toolbar-fields">
            <input v-model="keyword" placeholder="项目名称" @keydown.enter="runSearch" />
            <input v-model="dateKeyword" placeholder="时间关键字, 如 2025-07" @keydown.enter="runSearch" />
            <button class="dark-button small" type="button" @click="runSearch">筛选</button>
            <button class="gray-button small" type="button" @click="resetSearch">重置</button>
          </div>
        </div>

        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="notice error-notice">{{ error }}</p>

        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>项目</th>
                <th>数据时间</th>
                <th>流水规模</th>
                <th>创建信息</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in pagedProjects" :key="project.id">
                <td><strong>{{ project.name }}</strong></td>
                <td>{{ project.date_range }}</td>
                <td>{{ project.amount }}</td>
                <td>{{ project.creator }} · {{ project.created_at }}</td>
                <td><span :class="['status-badge', statusClass(project.status)]">{{ project.status }}</span></td>
                <td>
                  <div class="row-actions">
                    <RouterLink class="accent-button small" :to="`/bank/projects/${project.id}/recognition`">校验记录</RouterLink>
                    <RouterLink v-if="project.status === '已完成'" class="dark-button small" :to="`/bank/projects/${project.id}/report`">报告</RouterLink>
                    <button class="outline-button small" type="button" :disabled="project.status === '已完成' || actionKey === `review-${project.id}`" @click="markReviewed(project)">
                      {{ actionKey === `review-${project.id}` ? "提交中" : "复核完成" }}
                    </button>
                    <button class="danger-button small" type="button" :disabled="actionKey === `delete-${project.id}`" @click="deleteProject(project)">
                      {{ actionKey === `delete-${project.id}` ? "删除中" : "删除" }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="!loading && filteredProjects.length === 0" class="empty-state">没有匹配项目</p>
        </div>

        <div class="pagination">
          <span>第 {{ currentPage }} / {{ pages.length }} 页</span>
          <button v-for="page in pages" :key="page" :class="{ active: page === currentPage }" type="button" @click="currentPage = page">
            {{ page }}
          </button>
        </div>
      </main>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { createDemoProject, getProjects, removeProject, reviewProject, type ProjectItem } from "../api";
import PageShell from "../components/PageShell.vue";

const projects = ref<ProjectItem[]>([]);
const keyword = ref("");
const dateKeyword = ref("");
const notice = ref("");
const error = ref("");
const currentPage = ref(1);
const loading = ref(false);
const actionKey = ref("");
const pageSize = 8;

const filteredProjects = computed(() =>
  projects.value.filter((project) => {
    const keywordText = keyword.value.trim();
    const dateText = dateKeyword.value.trim();
    const nameMatched = !keywordText || project.name.includes(keywordText);
    const dateMatched = !dateText || project.date_range.includes(dateText) || project.created_at.includes(dateText);
    return nameMatched && dateMatched;
  })
);
const pagedProjects = computed(() => filteredProjects.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize));
const doneCount = computed(() => projects.value.filter((project) => project.status === "已完成").length);
const pendingCount = computed(() => projects.value.filter((project) => project.status !== "已完成").length);
const pages = computed(() => Array.from({ length: Math.max(1, Math.ceil(filteredProjects.value.length / pageSize)) }, (_, index) => index + 1));

function statusClass(status: string) {
  if (status === "已完成") return "status-done";
  if (status.includes("解析")) return "status-running";
  return "status-pending";
}

async function loadProjects(message = "") {
  loading.value = true;
  error.value = "";
  try {
    const data = await getProjects();
    projects.value = data.items;
    currentPage.value = Math.min(currentPage.value, pages.value.length);
    if (message) notice.value = message;
  } catch {
    error.value = "项目列表读取失败, 请确认后端服务可用。";
  } finally {
    loading.value = false;
  }
}

function runSearch() {
  currentPage.value = 1;
  notice.value = `筛选到 ${filteredProjects.value.length} 个项目`;
}

function resetSearch() {
  keyword.value = "";
  dateKeyword.value = "";
  currentPage.value = 1;
  notice.value = "筛选条件已重置";
}

async function addDemoProject() {
  actionKey.value = "create";
  try {
    await createDemoProject();
    await loadProjects("已上传示例文件并创建任务");
  } catch {
    error.value = "上传示例文件失败。";
  } finally {
    actionKey.value = "";
  }
}

async function markReviewed(project: ProjectItem) {
  actionKey.value = `review-${project.id}`;
  try {
    await reviewProject(project.id);
    await loadProjects(`${project.name} 已标记为复核完成`);
  } catch {
    error.value = "复核状态提交失败。";
  } finally {
    actionKey.value = "";
  }
}

async function deleteProject(project: ProjectItem) {
  actionKey.value = `delete-${project.id}`;
  try {
    await removeProject(project.id);
    await loadProjects(`已删除 ${project.name}`);
  } catch {
    error.value = "删除项目失败。";
  } finally {
    actionKey.value = "";
  }
}

onMounted(() => {
  void loadProjects();
});
</script>
