<template>
  <v-app>
    <v-main>
      <v-container fluid class="py-4">
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
              <v-col cols="12" md="3">
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
              <v-col cols="12" md="3">
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

              <!-- 费用/PP/DP 输入框筛选（恢复原样式） -->
              <v-col cols="12" md="2">
                <v-text-field
                  v-model.number="costMin"
                  label="费用≥"
                  type="number"
                  min="0"
                  @input="onFilterDebounced"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model.number="ppMin"
                  label="PP≥"
                  type="number"
                  min="0"
                  @input="onFilterDebounced"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model.number="dpMin"
                  label="DP≥"
                  type="number"
                  min="0"
                  @input="onFilterDebounced"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 卡牌网格（优化布局，确保显示） -->
        <v-row :cols="1" :sm="2" :md="3" :lg="4" :xl="5" class="g-4">
          <!-- 无数据提示 -->
          <v-col v-if="filteredCards.length === 0" class="text-center py-8">
            <v-icon size="64" class="text-gray-400 mb-2">mdi-card-text</v-icon>
            <p class="text-gray-500">暂无匹配的卡牌数据</p>
          </v-col>

          <!-- 卡牌列表 -->
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
                class="pa-2"
                contain
              ></v-img>
              <v-card-title class="text-center text-truncate py-2">
                {{ card.name }}
              </v-card-title>
              <v-card-subtitle class="text-center pb-2">
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

    <!-- 底部免责声明 -->
    <v-footer class="bg-gradient-to-r from-blue-900 to-gray-900 text-lighten-3 py-4">
      <v-container fluid>
        <v-row justify="center" class="mb-2">
          <v-col cols="12" class="text-center">
            PCG卡查是一个非官方粉丝工具，所有卡牌资料版权归 Bushiroad (武士道) 所有，本网站与 Bushiroad 并无任何官方合作或授权关系。
          </v-col>
        </v-row>
        <v-row justify="center" class="mb-3">
          <v-col cols="12" class="text-center">
            © 2025 PCG卡查. All rights reserved. 
            <span class="mx-2">|</span>
            <a href="#" class="text-blue-300 hover:underline">问题反馈</a>
          </v-col>
        </v-row>
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
const allCards = ref([]); 
const searchQuery = ref(''); 
const selectedSeries = ref(null); 
const selectedColors = ref([]); 
// 恢复为输入框绑定的数值（默认0）
const costMin = ref(0); 
const ppMin = ref(0); 
const dpMin = ref(0); 
const selectedCard = ref(null); 
const dialog = ref(false); 
const imagesBase = 'https://your-image-base-url.com/images'; // 替换为实际图片路径

// 系列列表
const seriesList = ref([
  { text: 'BP01', value: 'BP01' },
  { text: 'BP02', value: 'BP02' },
]);

// 防抖计时器
let t = null;
const onFilterDebounced = () => {
  clearTimeout(t);
  t = setTimeout(() => {
    console.log('筛选条件更新');
  }, 150);
};

// 图片URL生成
const imageUrl = (card) => {
  return `${imagesBase}/${card.id}.jpg`; 
};

// 打开详情弹窗
const openCardDetail = (card) => {
  selectedCard.value = card;
  dialog.value = true;
};

// 筛选逻辑（适配输入框）
const filteredCards = computed(() => {
  return allCards.value.filter(card => {
    // 关键词筛选
    const keywordMatch = 
      card.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (card.eff && card.eff.toLowerCase().includes(searchQuery.value.toLowerCase()));
    
    // 系列筛选
    const seriesMatch = selectedSeries.value ? card.series === selectedSeries.value : true;
    
    // 颜色筛选
    const colorMatch = selectedColors.value.length > 0 
      ? selectedColors.value.includes(card.color) 
      : true;
    
    // 数值筛选（兼容输入框空值）
    const costMatch = costMin.value === null || costMin.value === '' ? true : card.cost >= costMin.value;
    const ppMatch = ppMin.value === null || ppMin.value === '' ? true : card.PP >= ppMin.value;
    const dpMatch = dpMin.value === null || dpMin.value === '' ? true : card.DP >= dpMin.value;

    return keywordMatch && seriesMatch && colorMatch && costMatch && ppMatch && dpMatch;
  });
});

// 初始化数据
onMounted(async () => {
  try {
    // 测试用：手动添加数据（如果后端接口未就绪）
    allCards.value = [
      { id: 1, name: '测试卡牌1', series: 'BP01', color: '红', cost: 2, PP: 5, DP: 3, eff: '测试效果1' },
      { id: 2, name: '测试卡牌2', series: 'BP02', color: '蓝', cost: 3, PP: 7, DP: 4, eff: '测试效果2' }
    ];

    // 真实接口（替换上面的测试数据）
    // const res = await fetch('/api/search');
    // const data = await res.json();
    // allCards.value = data;

    // 自动提取系列列表
    const uniqueSeries = [...new Set(allCards.value.map(c => c.series))];
    seriesList.value = uniqueSeries.map(s => ({ text: s, value: s }));
  } catch (err) {
    console.error('获取数据失败：', err);
  }
});
</script>

<style scoped>
/* 优化卡片样式 */
.v-card {
  transition: transform 0.2s;
}
.v-card:hover {
  transform: translateY(-4px);
}

/* 链接样式 */
a {
  text-decoration: none;
}
</style>