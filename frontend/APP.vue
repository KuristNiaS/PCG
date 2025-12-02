<template>
  <v-app>
    <!-- 主体内容 -->
    <v-main>
      <v-container fluid class="py-4">
        <!-- 搜索栏、筛选面板、卡牌网格、弹窗 这些内容保持不变 -->
        <!-- 搜索栏 -->
        <v-card class="mb-4">
          <v-card-text>
            <v-text-field
              v-model="searchQuery"
              label="搜索卡牌名称/效果"
              placeholder="输入关键词..."
              prepend-inner-icon="mdi-magnify"
              @input="onFilterDebounced"
            ></v-text-field>
          </v-card-text>
        </v-card>

        <!-- 筛选面板 -->
        <v-card class="mb-4">
          <v-card-title>筛选条件</v-card-title>
          <v-card-text>
            <v-row>
              <!-- 系列筛选 -->
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedSeries"
                  label="选择系列"
                  :items="seriesList"
                  item-value="value"
                  item-text="text"
                  placeholder="全部系列"
                  clearable
                  @change="onFilterDebounced"
                ></v-select>
              </v-col>

              <!-- 颜色筛选 -->
              <v-col cols="12" md="4">
                <v-checkbox-group
                  v-model="selectedColors"
                  label="选择颜色"
                  @change="onFilterDebounced"
                >
                  <v-checkbox label="红" value="红"></v-checkbox>
                  <v-checkbox label="蓝" value="蓝"></v-checkbox>
                  <v-checkbox label="绿" value="绿"></v-checkbox>
                  <v-checkbox label="黑" value="黑"></v-checkbox>
                  <v-checkbox label="白" value="白"></v-checkbox>
                </v-checkbox-group>
              </v-col>
            </v-row>

            <!-- 滑块筛选：费用/PP/DP -->
            <v-row class="mt-4">
              <!-- 费用滑块 -->
              <v-col cols="12" sm="4">
                <div class="d-flex align-center">
                  <v-slider
                    v-model="costMin"
                    label="费用最小值"
                    :min="0"
                    :max="sliderMax.cost"
                    step="1"
                    show-ticks
                    ticks="always"
                    hide-details="auto"
                    class="flex-grow-1"
                    @change="onFilterDebounced"
                  ></v-slider>
                  <span class="ml-3">≥ {{ costMin }}</span>
                </div>
              </v-col>

              <!-- PP滑块 -->
              <v-col cols="12" sm="4">
                <div class="d-flex align-center">
                  <v-slider
                    v-model="ppMin"
                    label="PP最小值"
                    :min="0"
                    :max="sliderMax.pp"
                    step="1"
                    show-ticks
                    ticks="always"
                    hide-details="auto"
                    class="flex-grow-1"
                    @change="onFilterDebounced"
                  ></v-slider>
                  <span class="ml-3">≥ {{ ppMin }}</span>
                </div>
              </v-col>

              <!-- DP滑块 -->
              <v-col cols="12" sm="4">
                <div class="d-flex align-center">
                  <v-slider
                    v-model="dpMin"
                    label="DP最小值"
                    :min="0"
                    :max="sliderMax.dp"
                    step="1"
                    show-ticks
                    ticks="always"
                    hide-details="auto"
                    class="flex-grow-1"
                    @change="onFilterDebounced"
                  ></v-slider>
                  <span class="ml-3">≥ {{ dpMin }}</span>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 卡牌网格 -->
        <v-row :cols="12" :sm="2" :md="3" :lg="4" :xl="5" class="g-4">
          <v-col
            v-for="card in filteredCards"
            :key="card.id"
            class="d-flex"
          >
            <v-card
              class="flex-grow-1"
              hover
              @click="openCardDetail(card)"
            >
              <v-img 
                :src="imageUrl(card)" 
                aspect-ratio="450/629"  
                max-width="450"         
                cover
              ></v-img>
              <v-card-title class="text-center text-truncate">
                {{ card.name }}
              </v-card-title>
              <v-card-subtitle class="text-center">
                费用：{{ card.cost }} | PP：{{ card.PP }} | DP：{{ card.DP }}
              </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>

        <!-- 卡牌详情弹窗 -->
        <v-dialog
          v-model="dialog"
          max-width="500px"
        >
          <v-card v-if="selectedCard">
            <v-card-title class="text-h4">
              {{ selectedCard.name }}
            </v-card-title>
            <v-card-text>
              <v-img
                :src="imageUrl(selectedCard)"
                aspect-ratio="450/629"
                class="mb-4"
                contain
              ></v-img>
              <v-list>
                <v-list-item>
                  <v-list-item-title>系列：{{ selectedCard.series }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>颜色：{{ selectedCard.color }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>费用：{{ selectedCard.cost }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>PP：{{ selectedCard.PP }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>DP：{{ selectedCard.DP }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>效果：{{ selectedCard.eff }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
            <v-card-actions>
              <v-btn
                color="primary"
                @click="dialog = false"
              >
                关闭
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>

    <!-- 免责声明 Footer：放在 v-main 外面，作为 v-app 的直接子元素 -->
    <v-footer class="bg-gradient-to-r from-blue-900 to-gray-900 text-lighten-3 py-4">
      <v-container fluid>
        <!-- 免责声明 -->
        <v-row justify="center" class="mb-2">
          <v-col cols="12" class="text-center">
            PCG卡查是一个非官方粉丝工具，所有卡牌资料版权归 Bushiroad (武士道) 所有，本网站与 Bushiroad 并无任何官方合作或授权关系。
          </v-col>
        </v-row>

        <!-- 版权+问题反馈 -->
        <v-row justify="center" class="mb-3">
          <v-col cols="12" class="text-center">
            © 2025 PCG卡查. All rights reserved. 
            <span class="mx-2">|</span>
            <a href="#" class="text-blue-300 hover:underline">问题反馈</a>
          </v-col>
        </v-row>

        <!-- 开发者信息 -->
        <v-row justify="center" align="center">
          <v-col cols="12" class="text-center">
            <v-icon size="16" class="mr-1">mdi-code-tags</v-icon>
            Developed by KuristNiaS
            <span class="mx-3">|</span>
            <v-icon size="16" class="mr-1">mdi-palette</v-icon>
            PCG卡查团队
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

// 响应式变量
const allCards = ref([]); // 所有卡牌数据
const searchQuery = ref(''); // 搜索关键词
const selectedSeries = ref(null); // 选中的系列
const selectedColors = ref([]); // 选中的颜色
const costMin = ref(0); // 费用最小值（滑块）
const ppMin = ref(0); // PP最小值（滑块）
const dpMin = ref(0); // DP最小值（滑块）
const selectedCard = ref(null); // 选中的卡牌详情
const dialog = ref(false); // 弹窗控制
const imagesBase = 'https://your-image-base-url.com/images'; // 替换为你的图片基础路径

// 滑块最大值（根据你的卡牌数据调整）
const sliderMax = ref({
  cost: 10,
  pp: 20,
  dp: 30
});

// 系列列表（从后端获取或手动定义）
const seriesList = ref([
  { text: 'BP01', value: 'BP01' },
  { text: 'BP02', value: 'BP02' },
  // 补充你的其他系列
]);

// 防抖计时器
let t = null;

// 防抖过滤触发
const onFilterDebounced = () => {
  clearTimeout(t);
  t = setTimeout(() => {
    console.log('筛选条件更新');
  }, 150);
};

// 生成卡牌图片URL
const imageUrl = (card) => {
  return `${imagesBase}/${card.id}.jpg`; // 匹配你的图片命名规则
};

// 打开卡牌详情弹窗
const openCardDetail = (card) => {
  selectedCard.value = card;
  dialog.value = true;
};

// 筛选后的卡牌列表（核心计算属性）
const filteredCards = computed(() => {
  return allCards.value.filter(card => {
    // 关键词筛选（名称/效果）
    const keywordMatch = 
      card.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (card.eff && card.eff.toLowerCase().includes(searchQuery.value.toLowerCase()));

    // 系列筛选
    const seriesMatch = selectedSeries.value ? card.series === selectedSeries.value : true;

    // 颜色筛选（多选）
    const colorMatch = selectedColors.value.length > 0 
      ? selectedColors.value.includes(card.color) 
      : true;

    // 滑块筛选（费用/PP/DP）
    const costMatch = card.cost >= costMin.value;
    const ppMatch = card.PP >= ppMin.value;
    const dpMatch = card.DP >= dpMin.value;

    // 所有条件需同时满足
    return keywordMatch && seriesMatch && colorMatch && costMatch && ppMatch && dpMatch;
  });
});

// 初始化获取卡牌数据
onMounted(async () => {
  try {
    // 从后端API获取数据（替换为你的后端接口）
    const res = await fetch('/api/search');
    const data = await res.json();
    allCards.value = data;

    // 自动识别滑块最大值（可选，根据实际数据动态调整）
    if (data.length > 0) {
      sliderMax.value = {
        cost: Math.max(...data.map(c => c.cost)),
        pp: Math.max(...data.map(c => c.PP)),
        dp: Math.max(...data.map(c => c.DP))
      };
    }

    // 提取系列列表（可选，从数据中自动生成）
    const uniqueSeries = [...new Set(data.map(c => c.series))];
    seriesList.value = uniqueSeries.map(s => ({ text: s, value: s }));
  } catch (err) {
    console.error('获取卡牌数据失败：', err);
  }
});
</script>

<style scoped>
.v-slider {
  --v-slider-track-color: #2196f3;
  --v-slider-thumb-color: #1976d2;
}

/* 可选：给 footer 链接加 hover 效果 */
a {
  text-decoration: none;
  transition: color 0.2s;
}
</style>