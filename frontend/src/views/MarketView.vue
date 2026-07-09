<template>
  <PageShell>
    <section class="catalog-shell">
      <aside class="catalog-side">
        <span class="eyebrow">Workbench</span>
        <h1>智能流程目录</h1>
        <p>选择一个本地 demo 流程，查看上传、解析、比对、复核和报告链路。</p>
        <label class="catalog-search">
          <span>搜索</span>
          <input v-model="keyword" placeholder="输入流程名称或场景" />
        </label>
        <div class="catalog-tabs">
          <button
            v-for="item in departments"
            :key="item"
            :class="{ active: item === activeDepartment }"
            type="button"
            @click="activeDepartment = item"
          >
            {{ item }}
          </button>
        </div>
      </aside>

      <main class="catalog-main">
        <div class="catalog-bar">
          <div>
            <strong>{{ filteredAgents.length }} 个流程</strong>
            <span>{{ activeDepartment }} · {{ activeScene }}</span>
          </div>
          <div class="catalog-scene">
            <button
              v-for="item in scenes"
              :key="item"
              :class="{ active: item === activeScene }"
              type="button"
              @click="activeScene = item"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <p v-if="notice" class="notice">{{ notice }}</p>

        <section class="workflow-grid">
          <article v-for="agent in filteredAgents" :key="agent.id" class="workflow-card">
            <div class="workflow-mark">{{ agent.name.slice(0, 2) }}</div>
            <div>
              <span>{{ agent.department }} / {{ agent.scene }}</span>
              <h2>{{ agent.name }}</h2>
              <p>{{ agent.description }}</p>
            </div>
            <div class="workflow-meta">
              <span>{{ agent.views }} 次查看</span>
              <span>{{ favoriteCount(agent) }} 收藏</span>
              <span>{{ agent.likes }} 点赞</span>
            </div>
            <div class="workflow-actions">
              <RouterLink class="primary-button" :to="agent.route">进入流程</RouterLink>
              <button class="outline-button" type="button" @click="toggleFavorite(agent)">
                {{ favorites.has(agent.id) ? "已收藏" : "收藏" }}
              </button>
            </div>
          </article>
        </section>

        <section class="catalog-insights">
          <div>
            <strong>已脱敏</strong>
            <span>全部数据均为 mock 样例</span>
          </div>
          <div>
            <strong>三类流程</strong>
            <span>流水、制度、文档差异</span>
          </div>
          <div>
            <strong>本地运行</strong>
            <span>不依赖私有外部服务</span>
          </div>
        </section>
      </main>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getAgents, type AgentCard } from "../api";
import PageShell from "../components/PageShell.vue";

const departments = ["全部", "财务运营", "合规风控", "法务支持"];
const scenes = ["全部", "数据解析", "文档比对", "风险核查"];
const agents = ref<AgentCard[]>([]);
const activeDepartment = ref("全部");
const activeScene = ref("全部");
const keyword = ref("");
const favorites = ref(new Set<number>());
const notice = ref("");

const filteredAgents = computed(() =>
  agents.value.filter((agent) => {
    const departmentMatched = activeDepartment.value === "全部" || agent.department === activeDepartment.value;
    const sceneMatched = activeScene.value === "全部" || agent.scene === activeScene.value;
    const keywordText = keyword.value.trim();
    const keywordMatched = !keywordText || `${agent.name}${agent.description}${agent.scene}`.includes(keywordText);
    return departmentMatched && sceneMatched && keywordMatched;
  })
);

function favoriteCount(agent: AgentCard) {
  return agent.favorites + (favorites.value.has(agent.id) ? 1 : 0);
}

function toggleFavorite(agent: AgentCard) {
  const next = new Set(favorites.value);
  if (next.has(agent.id)) {
    next.delete(agent.id);
    notice.value = `已取消收藏 ${agent.name}`;
  } else {
    next.add(agent.id);
    notice.value = `已收藏 ${agent.name}`;
  }
  favorites.value = next;
}

onMounted(async () => {
  agents.value = await getAgents();
});
</script>
