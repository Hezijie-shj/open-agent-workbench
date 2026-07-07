<template>
  <PageShell :header="false" compact>
    <section class="review-board">
      <aside class="review-rail">
        <RouterLink to="/bank/projects" class="back-link compact-link">‹ 返回项目</RouterLink>
        <div class="rail-block">
          <span class="eyebrow">Batch</span>
          <h1>流水结构校验</h1>
          <p>{{ data?.file_name }}</p>
        </div>
        <div class="rail-stats">
          <button type="button" :class="{ active: focusMode === 'all' }" @click="focusMode = 'all'">
            <strong>{{ rows.length }}</strong>
            <span>全部记录</span>
          </button>
          <button type="button" :class="{ active: focusMode === 'issues' }" @click="showIssues">
            <strong>{{ issueCount }}</strong>
            <span>关注项</span>
          </button>
        </div>
        <div class="page-stack">
          <button
            v-for="page in pageButtons"
            :key="page"
            type="button"
            :class="{ active: page === currentPage }"
            @click="loadPage(page)"
          >
            Page {{ page }}
          </button>
        </div>
        <div class="rail-actions">
          <button type="button" :disabled="loadingAction === 'full'" @click="runFullPdf">
            {{ loadingAction === "full" ? "处理中..." : "完整 PDF 流程" }}
          </button>
          <button type="button" :disabled="loadingAction === 'fallback'" @click="runFallback">
            {{ loadingAction === "fallback" ? "检查中..." : "敏感词兜底" }}
          </button>
        </div>
      </aside>

      <main class="document-stage">
        <div class="stage-toolbar">
          <div>
            <strong>文档画布</strong>
            <span>{{ selectedRow ? `已定位 source ${selectedRow.source_ids?.join(", ")}` : "选择右侧记录查看来源区域" }}</span>
          </div>
          <div class="tool-buttons">
            <button type="button" @click="zoom = Math.min(1.35, zoom + 0.1)">⊕</button>
            <button type="button" @click="zoom = Math.max(0.75, zoom - 0.1)">⊖</button>
            <button type="button" @click="rotation = (rotation + 90) % 360">↻</button>
            <button type="button" @click="resetPreview">还原</button>
          </div>
        </div>

        <div class="document-canvas">
          <div class="statement-page" :style="{ transform: `scale(${zoom}) rotate(${rotation}deg)` }">
            <div class="statement-head">
              <span>账户明细对账单</span>
              <small>Page {{ currentPage }} / {{ data?.total_pages || 1 }}</small>
            </div>
            <div class="statement-account">
              <span>户名：星河样例科技有限公司</span>
              <span>账号：6222 **** **** 0000</span>
            </div>
            <div class="statement-grid">
              <div class="statement-row statement-title">
                <span>序号</span><span>交易时间</span><span>摘要</span><span>借方</span><span>贷方</span><span>余额</span>
              </div>
              <button
                v-for="(item, index) in rows"
                :key="item.id"
                type="button"
                :class="['statement-row', selectedIndex === index ? 'pdf-row-active' : '', item.issue ? 'pdf-row-issue' : '']"
                @click="selectRow(index, 'pdf')"
              >
                <span>{{ item.id }}</span>
                <span>{{ item.date }}</span>
                <span>{{ item.counterparty || "示例对手方" }}</span>
                <span>{{ item.type === "支出" ? item.amount : "--" }}</span>
                <span>{{ item.type === "收入" ? item.amount : "--" }}</span>
                <span>{{ item.balance }}</span>
              </button>
            </div>
            <div
              v-if="selectedRow?.bbox"
              class="source-box"
              :style="boxStyle(selectedRow.bbox)"
            ></div>
            <div
              v-for="(box, index) in issueBoxes"
              :key="index"
              class="source-box issue-box"
              :style="boxStyle(box)"
            ></div>
          </div>
        </div>
      </main>

      <aside class="data-inspector">
        <div class="inspector-head">
          <div>
            <strong>结构化记录</strong>
            <span>{{ filteredRows.length }} 条</span>
          </div>
          <button class="outline-button small" type="button" :disabled="loadingAction === 'rerun'" @click="rerunRecognition">
            {{ loadingAction === "rerun" ? "识别中" : "重新识别" }}
          </button>
        </div>

        <div class="record-list">
          <button
            v-for="(item, index) in filteredRows"
            :key="item.id"
            type="button"
            :class="['record-card', rows.indexOf(item) === selectedIndex ? 'active' : '']"
            @mouseenter="selectRow(rows.indexOf(item), 'table')"
            @click="selectRow(rows.indexOf(item), 'table')"
          >
            <span class="record-topline">
              <strong>{{ item.date }}</strong>
              <em :class="item.type === '收入' ? 'green' : 'red'">{{ item.amount }}</em>
            </span>
            <span>{{ item.counterparty || "示例对手方" }} · 余额 {{ item.balance }}</span>
            <small>
              {{ item.source_ids?.join(" / ") }}
              <b v-if="item.issue"> · {{ item.issue }}</b>
            </small>
          </button>
        </div>

        <div class="field-card" v-if="selectedRow">
          <h2>字段详情</h2>
          <dl>
            <dt>交易类型</dt><dd>{{ selectedRow.type }}</dd>
            <dt>置信度</dt><dd>{{ Math.round((selectedRow.confidence || 0.92) * 100) }}%</dd>
            <dt>Source IDs</dt><dd>{{ selectedRow.source_ids?.join(", ") }}</dd>
            <dt>坐标框</dt><dd>{{ selectedRow.bbox?.join(", ") }}</dd>
          </dl>
          <div class="inspector-actions">
            <button class="accent-button" type="button" @click="confirmEdit">确认记录</button>
            <button class="danger-button" type="button" @click="deleteRow(selectedIndex)">删除</button>
          </div>
        </div>

        <p v-if="notice" class="notice compact-notice">{{ notice }}</p>
        <button class="primary-button inspector-download" type="button" @click="downloadResult">下载 JSON</button>
      </aside>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getAnalysisResult, getFullPdfRecognition, getSensitiveFallback, getSinglePageRecognition, type TransactionItem } from "../api";
import PageShell from "../components/PageShell.vue";
import { downloadJson } from "../utils";

const route = useRoute();
const data = ref<any>();
const selectedIndex = ref(0);
const currentPage = ref(1);
const zoom = ref(1);
const rotation = ref(0);
const notice = ref("");
const focusMode = ref<"all" | "issues">("all");
const loadingAction = ref("");

const rows = computed<TransactionItem[]>(() => (data.value?.items || []).map((item: TransactionItem, index: number) => normalizeRow(item, index)));
const filteredRows = computed(() => (focusMode.value === "issues" ? rows.value.filter((item) => item.issue) : rows.value));
const selectedRow = computed(() => rows.value[selectedIndex.value]);
const issueCount = computed(() => rows.value.filter((item) => item.issue).length);
const issueBoxes = computed(() => rows.value.filter((item, index) => item.issue && index !== selectedIndex.value).map((item) => item.bbox).filter(Boolean) as [number, number, number, number][]);
const pageButtons = computed(() => Array.from({ length: data.value?.total_pages || 1 }, (_, index) => index + 1).slice(0, 6));

function normalizeRow(item: TransactionItem, index: number): TransactionItem {
  const top = 190 + index * 58;
  return {
    ...item,
    counterparty: item.counterparty || ["晨星材料样例", "北桥工程样例", "云舟信息样例", "星河经营账户"][index % 4],
    source_ids: item.source_ids || [`T${item.id}-D`, `T${item.id}-A`, `T${item.id}-B`],
    bbox: item.bbox || [48, top, 672, top + 42],
    confidence: item.confidence || (item.amount.startsWith("-") ? 0.86 : 0.94),
    issue: item.issue || (item.amount.startsWith("-") ? "支出需复核" : "")
  };
}

async function loadPage(page: number) {
  loadingAction.value = "page";
  try {
    const result = await getAnalysisResult(String(route.params.id), page);
    data.value = { ...result, page };
    currentPage.value = page;
    selectedIndex.value = 0;
  } catch {
    notice.value = "识别结果读取失败, 请确认后端服务可用";
  } finally {
    loadingAction.value = "";
  }
}

function changePage(offset: number) {
  const total = data.value?.total_pages || 1;
  const next = Math.min(total, Math.max(1, currentPage.value + offset));
  void loadPage(next);
  notice.value = `已切换到第 ${next} 页`;
}

function selectRow(index: number, source: "pdf" | "table") {
  selectedIndex.value = Math.max(0, index);
  const row = rows.value[selectedIndex.value];
  notice.value = source === "pdf" ? `已从文档定位记录 ${row?.id}` : `已同步高亮 PDF 区域 ${row?.source_ids?.join(", ")}`;
}

function resetPreview() {
  zoom.value = 1;
  rotation.value = 0;
  notice.value = "预览已还原";
}

function showIssues() {
  focusMode.value = "issues";
  const index = rows.value.findIndex((item) => item.issue);
  selectedIndex.value = Math.max(0, index);
  notice.value = issueCount.value ? `已定位到 ${issueCount.value} 条支出类关注项` : "当前页未发现关注项";
}

function confirmAudit() {
  notice.value = "当前页已确认审核";
}

async function rerunRecognition() {
  loadingAction.value = "rerun";
  try {
    const result = await getSinglePageRecognition(String(route.params.id), currentPage.value);
    data.value = { ...result, page: currentPage.value };
    selectedIndex.value = 0;
    notice.value = result.sensitive_fallback?.used ? "已重新识别, 并触发敏感词兜底回填" : "已完成单页重新识别";
  } catch {
    notice.value = "重新识别失败, 请确认后端服务可用";
  } finally {
    loadingAction.value = "";
  }
}

async function runFullPdf() {
  loadingAction.value = "full";
  try {
    const result = await getFullPdfRecognition(String(route.params.id));
    notice.value = `完整 PDF 流程完成: ${result.summary.row_count} 条记录, ${result.summary.recognized_pages}/${result.summary.total_pages} 页有结果`;
  } catch {
    notice.value = "完整 PDF 流程读取失败, 请确认后端服务可用";
  } finally {
    loadingAction.value = "";
  }
}

async function runFallback() {
  loadingAction.value = "fallback";
  try {
    const result = await getSensitiveFallback(String(route.params.id), currentPage.value);
    notice.value = result.used ? `敏感词兜底已启用, 回填 ${result.recovered_row_count} 条记录` : "当前页未触发敏感词兜底";
  } catch {
    notice.value = "敏感词兜底检查失败, 请确认后端服务可用";
  } finally {
    loadingAction.value = "";
  }
}

function confirmEdit() {
  notice.value = `已确认 ${data.value?.items?.length || 0} 条结构化记录`;
}

function deleteRow(index: number) {
  data.value.items.splice(index, 1);
  selectedIndex.value = Math.max(0, Math.min(selectedIndex.value, data.value.items.length - 1));
  notice.value = "已删除一条识别结果";
}

function boxStyle(box: [number, number, number, number]) {
  const [x1, y1, x2, y2] = box;
  return {
    left: `${x1}px`,
    top: `${y1}px`,
    width: `${x2 - x1}px`,
    height: `${y2 - y1}px`
  };
}

function downloadResult() {
  downloadJson(`recognition-page-${currentPage.value}.json`, data.value);
  notice.value = "已生成结构化结果 JSON";
}

onMounted(async () => {
  await loadPage(1);
});
</script>
