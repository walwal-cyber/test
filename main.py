import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# -----------------------------------------------------------
# 1. AI 텍스처/스타일 시뮬레이션 함수
# 실제 AI 모델은 여기에 통합되어야 하지만, 예시에서는 Matplotlib 스타일을 사용합니다.
# -----------------------------------------------------------



def get_simulated_ai_style(style_name):
    """
    사용자가 선택한 'AI 스타일'에 따라 색상과 패턴을 반환합니다.
    실제 프로젝트에서는 외부 API나 로컬 모델을 호출하여 텍스처 이미지를 생성합니다.
    """
    styles = {
        "기본 - 정형 패턴": {"facecolor": "#E5E5E5", "edgecolor": "black", "hatch": None},
        "AI 스타일 1: 아르데코": {"facecolor": "#C49A6C", "edgecolor": "#4A3B2A", "hatch": "++", "linewidth": 2},
        "AI 스타일 2: 딥 오션": {"facecolor": "#4682B4", "edgecolor": "#191970", "hatch": "///", "linewidth": 1},
        "AI 스타일 3: 네오 팝": {"facecolor": "#FF69B4", "edgecolor": "#32CD32", "hatch": "oo", "linewidth": 0.5},
    }
    return styles.get(style_name, styles["기본 - 정형 패턴"])

# -----------------------------------------------------------
# 2. 에셔 스타일 변환 (평행이동) 구현 함수
# -----------------------------------------------------------
def create_escher_tile(width, height, offset_x, offset_y):
    """
    정사각형 타일(0,0)에서 (width, height)를 기반으로 평행이동 변환을 적용하여
    비정형 타일의 좌표(꼭짓점)를 생성합니다. (사각형의 한 변에 '돌출부'를 만듭니다.)
    """
    # 1. 기본 정사각형의 꼭짓점: (0,0) -> (w,0) -> (w,h) -> (0,h)
    base_coords = np.array([
        [0.0, 0.0],  # Bottom Left (BL)
        [width, 0.0], # Bottom Right (BR)
        [width, height], # Top Right (TR)
        [0.0, height], # Top Left (TL)
    ])

    # 2. 상단 변 (TL-TR)에 적용할 '돌출부' 좌표 (삼각형 모양으로 단순화)
    # 돌출부 기준점은 상단 변의 중점: (width/2, height)
    mid_point = [width / 2, height]
    bump_point = [mid_point[0] + offset_x, mid_point[1] + offset_y]

    # 3. 비정형 타일의 좌표 순서 정의 (5개 꼭짓점)
    # TL -> BUMP -> TR -> BR -> BL
    transformed_coords = np.array([
        base_coords[3],  # TL (0, h)
        bump_point,      # BUMP
        base_coords[2],  # TR (w, h)
        base_coords[1],  # BR (w, 0)
        base_coords[0],  # BL (0, 0)
    ])
    
    # 4. 상단 변의 변형을 평행이동하여 하단 변 (BL-BR)에 적용
    # 평행이동 벡터: (0, -height)
    # 여기서는 상단 변만 변형하고, 테셀레이션 시 자동으로 연결되도록 단순화합니다.
    # 복잡한 에셔 변환(좌표를 더 늘려야 함)은 심화 과정으로 남겨둡니다.

    return transformed_coords

# -----------------------------------------------------------
# 3. 테셀레이션 패턴 그리기 함수
# -----------------------------------------------------------
def draw_tessellation(ax, tile_coords, cols, rows, style):
    """주어진 타일 좌표로 지정된 행/열만큼 평면을 덮습니다."""
    w = tile_coords[2, 0] - tile_coords[3, 0] # 타일 폭 (width)
    h = tile_coords[3, 1] - tile_coords[0, 1] # 타일 높이 (height)

    # Matplotlib Path 객체 생성
    # Path.LINETO (3)는 선을 긋고, Path.CLOSEPOLY (79)는 다각형을 닫습니다.
    tile_codes = [Path.MOVETO] + [Path.LINETO] * (len(tile_coords) - 1) + [Path.CLOSEPOLY]
    tile_coords = np.vstack([tile_coords, tile_coords[0]])
    
    # 격자 무늬로 반복
    for i in range(-cols // 2, cols // 2 + 1):
        for j in range(-rows // 2, rows // 2 + 1):
            
            # 타일의 기준 위치 (평행이동)
            offset = np.array([i * w, j * h])
            
            # 평행이동된 타일 좌표
            tiled_coords = tile_coords + offset
            
            # Matplotlib Path 객체 생성 및 그리기
            path = Path(tiled_coords, tile_codes)
            patch = PathPatch(path, **style, alpha=0.8) # AI 스타일 적용
            ax.add_patch(patch)

    # 축 설정
    ax.set_xlim(-w * cols / 2, w * cols / 2 + w)
    ax.set_ylim(-h * rows / 2, h * rows / 2 + h)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

# -----------------------------------------------------------
# 4. Streamlit UI 구성
# -----------------------------------------------------------

st.set_page_config(layout="wide", page_title="AI 테셀레이션 디자이너")
st.title("📐 AI 융합 테셀레이션 디자이너 (영재학교 프로젝트)")
st.caption("**수학 원리 (에셔 변환) + 파이썬 코딩 + AI 스타일 시뮬레이션**")

# --- 사이드바: 입력 제어 ---
st.sidebar.header("1. 테셀레이션 수학적 원리 (변환)")
st.sidebar.markdown("**기본 다각형:** 100x100 정사각형")

# 변환 파라미터 입력
st.sidebar.subheader("에셔 스타일 변환: 평행이동")
offset_x = st.sidebar.slider("X축 돌출/함몰 정도 (offset_x)", -30.0, 30.0, 0.0, 5.0)
offset_y = st.sidebar.slider("Y축 돌출/함몰 정도 (offset_y)", -30.0, 30.0, 20.0, 5.0)

st.sidebar.header("2. AI 시각적 강화 (스타일)")
# AI 스타일 선택
ai_style_options = ["기본 - 정형 패턴", "AI 스타일 1: 아르데코", "AI 스타일 2: 딥 오션", "AI 스타일 3: 네오 팝"]
selected_style = st.sidebar.selectbox("AI 생성 스타일 선택:", ai_style_options)

# 격자 크기
st.sidebar.header("3. 반복 격자 설정")
cols = st.sidebar.slider("가로 타일 개수", 3, 10, 6)
rows = st.sidebar.slider("세로 타일 개수", 3, 10, 6)


# --- 메인 영역: 결과 시각화 ---
st.subheader("테셀레이션 패턴 결과")

# 1. 스타일 및 타일 좌표 계산
tile_width = 100
tile_height = 100
final_tile_coords = create_escher_tile(tile_width, tile_height, offset_x, offset_y)
final_style = get_simulated_ai_style(selected_style)

# 2. Matplotlib 그래프 생성
fig, ax = plt.subplots(figsize=(10, 10))
draw_tessellation(ax, final_tile_coords, cols, rows, final_style)

# Safe Way to use Matplotlib in Streamlit
fig, ax = plt.subplots(figsize=(10, 10))
# ... drawing code using ax ...
st.pyplot(fig)


# 3. Streamlit에 그래프 표시
st.pyplot(fig)

# --- 코드 설명 및 분석 ---
st.markdown("---")
st.subheader("👨‍💻 프로젝트 분석을 위한 개발자 섹션")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. 수학적 변환 (타일 좌표)")
    st.code(f"""
# 기본 정사각형 (Bottom Left: (0,0), Top Right: (100, 100))
# 에셔 스타일 변환이 적용된 비정형 타일의 꼭짓점 좌표 (5개)
# [TL, BUMP, TR, BR, BL] 순서

{final_tile_coords}
    """, language="python")
    st.markdown("""
    학생들은 **`create_escher_tile`** 함수를 분석하며, 평행이동(Translation) 변환이 각 꼭짓점의 좌표에 어떻게 영향을 주어 
    비정형 타일이 탄생하고, 이것이 평면을 빈틈없이 덮는 수학적 원리를 이해해야 합니다.
    """)

with col2:
    st.markdown("### 2. AI 스타일 적용 (시뮬레이션)")
    st.code(f"""
# 선택된 AI 스타일 ('{selected_style}')의 속성
# 이 속성으로 Matplotlib 패치(Patch)가 렌더링됩니다.

{{
    'facecolor': '{final_style.get('facecolor')}',
    'edgecolor': '{final_style.get('edgecolor')}',
    'hatch': '{final_style.get('hatch')}',
}}
    """, language="python")
    st.markdown("""
    **`get_simulated_ai_style`** 함수는 실제 프로젝트에서 **AI 모델**을 호출하는 역할을 대신합니다. 
    학생들은 생성된 AI 이미지를 분석하여 수학적 패턴과 시각적 스타일의 조화를 평가합니다.
    """)
