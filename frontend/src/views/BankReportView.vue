<template>
  <PageShell :header="false" compact>
    <section class="audit-report">
      <div class="report-aside">
        <RouterLink to="/bank/projects" class="back-link compact-link">‹ 返回任务</RouterLink>
        <span class="eyebrow">Audit Report</span>
        <h1>{{ report?.project_name }}</h1>
        <p>{{ report?.date_range }}</p>
        <button class="primary-button" type="button" :disabled="!report" @click="downloadReport">下载报告 JSON</button>
      </div>

      <div class="report-summary">
        <div class="summary-tile">
          <span>核查主体</span>
          <strong>{{ report?.overview.subject }}</strong>
        </div>
        <div class="summary-tile">
          <span>日均余额</span>
          <strong class="blue">{{ report?.overview.avg_balance }}</strong>
        </div>
        <div class="summary-tile">
          <span>流入总额</span>
          <strong class="green">{{ report?.overview.income }}</strong>
        </div>
        <div class="summary-tile">
          <span>流出总额</span>
          <strong class="red">{{ report?.overview.expense }}</strong>
        </div>
      </div>
    </section>

    <p v-if="notice" class="notice">{{ notice }}</p>
    <p v-if="error" class="notice error-notice">{{ error }}</p>

    <section class="report-workspace">
      <article class="integrity-panel">
        <h2>连续性核查</h2>
        <div class="timeline-strip">
          <span></span><span></span><span class="warn"></span><span></span><span></span>
        </div>
        <dl>
          <dt>核查账号</dt><dd>{{ report?.overview.account }}</dd>
          <dt>数据范围</dt><dd>{{ report?.integrity.period }}</dd>
          <dt>数据时长</dt><dd>{{ report?.integrity.duration }}</dd>
          <dt>余额连续性</dt><dd class="red">{{ report?.integrity.status }}</dd>
        </dl>
      </article>

      <article class="composition-panel">
        <h2>流水构成</h2>
        <div class="composition-list">
          <button v-for="row in incomeRows" :key="row.type" type="button" :disabled="drawerLoading" @click="openDrawer(row.type, row.amount, '流入')">
            <span>{{ row.type }}</span><strong class="green">{{ row.amount }}</strong><em>{{ row.ratio }}</em>
          </button>
          <button v-for="row in expenseRows" :key="row.type" type="button" :disabled="drawerLoading" @click="openDrawer(row.type, row.amount, '流出')">
            <span>{{ row.type }}</span><strong class="red">{{ row.amount }}</strong><em>{{ row.ratio }}</em>
          </button>
        </div>
      </article>

      <article class="counterparty-panel">
        <h2>对手方分析</h2>
        <div class="counterparty-list">
          <button v-for="item in report?.counterparties || []" :key="item.name" type="button" :disabled="drawerLoading" @click="openDrawer(item.name, item.income, '对手方')">
            <span>
              <strong>{{ item.name }}</strong>
              <small>{{ item.related ? "样例关联方" : item.suspicious ? "样例关注方" : "普通对手方" }}</small>
            </span>
            <em class="blue">{{ item.income }}</em>
          </button>
        </div>
      </article>
    </section>

    <div v-if="drawerOpen" class="drawer-mask" @click.self="drawerOpen = false">
      <aside class="detail-drawer">
        <header>
          <div>
            <span class="eyebrow">{{ drawerKind }}</span>
            <h2>{{ detailTitle }}</h2>
          </div>
          <button class="outline-button small" type="button" @click="drawerOpen = false">关闭</button>
        </header>
        <table class="drawer-table">
          <thead>
            <tr><th>交易时间</th><th>对手方</th><th>类型</th><th>金额</th><th>余额</th></tr>
          </thead>
          <tbody>
            <tr v-if="drawerLoading"><td colspan="5">正在读取明细...</td></tr>
            <tr v-for="item in drawerRows" :key="item.id">
              <td>{{ item.date }}</td>
              <td>{{ item.counterparty }}</td>
              <td>{{ item.type }}</td>
              <td :class="item.type === '收入' ? 'green' : 'red'">{{ item.amount }}</td>
              <td>{{ item.balance }}</td>
            </tr>
          </tbody>
        </table>
        <div class="drawer-summary">
          <span>当前分类合计</span>
          <strong>{{ drawerAmount }}</strong>
        </div>
      </aside>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getReport, getReportDetails } from "../api";
import PageShell from "../components/PageShell.vue";
import { downloadJson } from "../utils";

const route = useRoute();
const report = ref<any>();
const notice = ref("");
const error = ref("");
const detailTitle = ref("");
const drawerOpen = ref(false);
const drawerKind = ref("");
const drawerAmount = ref("");
const drawerRows = ref<any[]>([]);
const drawerLoading = ref(false);

const incomeRows = computed(() => report.value?.composition.income || []);
const expenseRows = computed(() => report.value?.composition.expense || []);

function downloadReport() {
  if (!report.value) return;
  downloadJson("statement-report.json", report.value);
  notice.value = "已生成报告 JSON";
}

async function openDrawer(title: string, amount: string, kind: string) {
  detailTitle.value = `${title}流水明细`;
  drawerKind.value = kind;
  drawerAmount.value = amount;
  drawerOpen.value = true;
  drawerLoading.value = true;
  error.value = "";
  try {
    drawerRows.value = await getReportDetails(String(route.params.id), title);
    notice.value = `已打开 ${title} 的抽屉明细`;
  } catch {
    drawerRows.value = [];
    error.value = "流水明细读取失败, 请确认后端服务可用。";
  } finally {
    drawerLoading.value = false;
  }
}

onMounted(async () => {
  try {
    report.value = await getReport(String(route.params.id));
  } catch {
    error.value = "报告读取失败, 请确认项目已完成并且后端服务可用。";
  }
});
</script>
