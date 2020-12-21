import numpy as np
import pandas as pd


def data_cleansing(data, location_name):

    data = data.rename(columns={'پیمان': 'نام پیمان'})

    data = pd.merge(
        left=data,
        right=location_name[["نام", "منطقه", "ناحیه", "پیمان"]],
        how="left",
        left_on="نام پیمان",
        right_on="نام",
    ).drop("نام", axis=1)

    data["منطقه"] = data["منطقه"].astype(str).str.zfill(2)
    data["ناحیه"] = data["ناحیه"].astype(str).str.zfill(2)
    data["پیمان"] = data["پیمان"].astype(str).str.zfill(2)

    data = data.drop_duplicates(subset=list(data.columns)[1:], keep="first")

    # EXTRACT ADDRESS
    tmp = data.groupby(["منطقه", "ناحیه", "پیمان"])["نام لکه"].value_counts(dropna=False, sort=False)
    tmp = pd.DataFrame(tmp).rename(columns={"نام لکه": "تعداد"}).reset_index()

    Address = []

    for R in list(tmp["منطقه"].unique()):
        tmpR = tmp[tmp["منطقه"] == R]
        for D in list(tmpR["ناحیه"].unique()):
            tmpD = tmpR[tmpR["ناحیه"] == D]
            for P in list(tmpD["پیمان"].unique()):
                tmpP = tmpD[tmpD["پیمان"] == P]
                Address += list(range(1, len(tmpP) + 1))

    tmp["آدرس"] = Address
    tmp["آدرس"] = tmp["آدرس"].astype(str).str.zfill(3)

    tmp = tmp[["منطقه", "ناحیه", "پیمان", "نام لکه", "آدرس"]]

    data = pd.merge(left=data,
                    right=tmp,
                    how="left",
                    on=["منطقه", "ناحیه", "پیمان", "نام لکه"])

    data = data.sort_values(['منطقه', 'ناحیه', 'پیمان', 'آدرس'])

    # METER ERROR MODIFY
    data = data.drop(data[(data["نوع قلم"] == "درخت و درختچه") & (data["زیرمجموعه هر قلم"] == "متر")].index)

    # SPOT CLASS
    SPOT_CLASS = {
        "میادین": "01",
        "لچکی ها": "02",
        "آیلند های بزرگراه": "03",
        "آیلند ها": "04",
        "حاشیه های بزرگراه": "05",
        "حاشیه معابر": "06",
        "بوستان خطی": "07",
        "پارک های زیر 6 هکتار": "08",
        "پارک های بین 6 تا 10 هکتار": "09",
        "پارک های بالای 10 هکتار": "10",
        "جنگل کاری داخل محدوده": "11",
        "کمربندی": "12",
        "کمربند سبز حفاظتی": "13",
    }

    tmp = data["نوع لکه"].value_counts(dropna=False, sort=True).reset_index()

    tmp = tmp.rename(columns={"index": "نام نوع لکه",
                              "نوع لکه": "تعداد رکورد"})

    tmp["نوع لکه"] = list(map(SPOT_CLASS.get, tmp["نام نوع لکه"]))

    tmp = tmp[["نوع لکه", "نام نوع لکه", "تعداد رکورد"]]

    data.rename(columns={'نوع لکه': 'نام نوع لکه'}, inplace=True)

    data = pd.merge(
        left=data,
        right=tmp[["نوع لکه", "نام نوع لکه"]],
        how="left",
        on=["نام نوع لکه"]
    )

    # ITEM CLASS
    Item_Class = {
        "چمن": "01",
        "گل دائم باغچه های معمولی": "02",
        "گل دائم فلاورباکسهای سطوح شیب دار": "03",
        "گل فصل باغچه های معمولی": "04",
        "گل فصل فلاورباکس های سطوح شیب دار": "05",
        "پرچین": "06",
        "درخت و درختچه": "07",
        "درختان جنگلی": "08",
        "حفظ و نگهداری چمن": "51",
        "حفظ و نگهداری گل دائمی": "52",
        "حفظ و نگهداری سطوح شیبدار گل دائمی": "53",
        "حفظ و نگهداری گل فصلی": "54",
        "حفظ و نگهداری سطوح شیبدار گل فصلی": "55",
        "حفظ و نگهداری پرچین": "56",
        "حفظ و نگهداری درخت و درختچه": "57",
        "معابر": "91",
        "محوطه بازي كودكان": "92",
        "فضاهاي مسقف": "93",
        "آبنما نظافت": "94"
    }

    tmp = data["نوع قلم"].value_counts(dropna=False, sort=True).reset_index()

    tmp = tmp.rename(columns={"index": "نام نوع قلم",
                              "نوع قلم": "تعداد رکورد"})

    tmp["نوع قلم"] = list(map(Item_Class.get, tmp["نام نوع قلم"]))

    tmp = tmp[["نوع قلم", "نام نوع قلم", "تعداد رکورد"]].sort_values(["نوع قلم"]).reset_index(drop=True)

    tmp = tmp[["نوع قلم", "نام نوع قلم"]]

    data.rename(columns={'نوع قلم' : 'نام نوع قلم'}, inplace=True)

    data = pd.merge(
        left=data,
        right=tmp,
        how="left",
        on=["نام نوع قلم"]
    )

    # SUBITEM CLASS
    Subitem_Class = {
        "آبیاری ثقلی": "01",
        "آبیاری تانکری": "02",
        "آبیاری شلنگی": "03",
        "آبیاری تحت فشار": "04",
        "سایر گل های دائمی": "05",
        "گل رز": "06",
        "متر مربع": "07",
        "اصله": "08",
    }

    tmp = data["زیرمجموعه هر قلم"].value_counts(dropna=False, sort=True).reset_index()

    tmp = tmp.rename(columns={"index": "نام زیرمجموعه هر قلم",
                              "زیرمجموعه هر قلم": "تعداد رکورد"})

    tmp["زیرمجموعه هر قلم"] = list(map(Subitem_Class.get, tmp["نام زیرمجموعه هر قلم"]))

    tmp = tmp[["زیرمجموعه هر قلم", "نام زیرمجموعه هر قلم"]].sort_values(["زیرمجموعه هر قلم"]).reset_index(drop=True)

    data.rename(columns={'زیرمجموعه هر قلم': 'نام زیرمجموعه هر قلم'}, inplace=True)

    data = pd.merge(
        left=data,
        right=tmp[["زیرمجموعه هر قلم", "نام زیرمجموعه هر قلم"]],
        how="left",
        on=["نام زیرمجموعه هر قلم"]
    )

    # ID GENERATE
    data["شناسه"] = (
            data["منطقه"]
            + "."
            + data["ناحیه"]
            + "."
            + data["پیمان"]
            + "."
            + data["آدرس"]
            + "."
            + data["نوع لکه"]
            + "-"
            + data["نوع قلم"]
            + "."
            + data["زیرمجموعه هر قلم"]
    )

    # DROP NA ID
    data = data.dropna(subset=["شناسه"])

    # DUPLICATE ID
    tmp = data.groupby(["شناسه"]).agg({"نمایش آخرین ریزمتره (ریزمتره نهایی)": "sum",
                                        "مقدار در صورتجلسه تحویل و تحول": "sum"}).reset_index()

    data = data.drop_duplicates(subset="شناسه", keep="first")

    data = pd.merge(
        left=data,
        right=tmp,
        how="left",
        on="شناسه").drop(["مقدار در صورتجلسه تحویل و تحول_x", "نمایش آخرین ریزمتره (ریزمتره نهایی)_x"],
                         axis=1)

    data = data.rename(
        columns={"نمایش آخرین ریزمتره (ریزمتره نهایی)_y": "نمایش آخرین ریزمتره (ریزمتره نهایی)",
                 "مقدار در صورتجلسه تحویل و تحول_y": "مقدار در صورتجلسه تحویل و تحول"}
    )

    # RENAME COLUMNS NAME
    data.rename(
        columns={
            "نمایش آخرین ریزمتره (ریزمتره نهایی)": "مقدار آیتم",
            "مساحت لکه (مترمربع)": "مساحت آدرس",
            "مساحت پیمان (مترمربع)": "مساحت پیمان",
            "مقدار در صورتجلسه تحویل و تحول": "مقدار آیتم خام",
        },
        inplace=True,
    )

    data = data[
        [
            "شناسه",
            "منطقه",
            "ناحیه",
            "پیمان",
            "آدرس",
            "نوع لکه",
            "نوع قلم",
            "زیرمجموعه هر قلم",
            "مقدار آیتم",
            "مساحت آدرس",
            "مساحت پیمان",
            "نوع آیتم",
            "نام پیمان",
            "نام لکه",
            "نام نوع لکه",
            "نام نوع قلم",
            "نام زیرمجموعه هر قلم",
            "مقدار آیتم خام"
        ]
    ]

    data.sort_values(by=['منطقه', 'ناحیه', 'پیمان', 'آدرس'], ascending=True, inplace=True)

    data.reset_index(drop=True, inplace=True)

    return data


def tree_area_modify(data):

    result = pd.DataFrame(columns=data.columns)

    for idf, df in data.groupby(["منطقه", "ناحیه", "پیمان", "آدرس"]):
        df = df.reset_index(drop=True)
        TI_Check = df.query('`نوع قلم` == "07" and `زیرمجموعه هر قلم` == ["01", "02", "03", "04"]').shape[0]
        TI_Index = df.query('`نوع قلم` == "07" and `زیرمجموعه هر قلم` == ["01", "02", "03", "04"]').index.to_list()

        if TI_Check > 0:
            tree_area = 9
            Independent_Tree = df.query('`نوع قلم` == "07" and `زیرمجموعه هر قلم` == ["01", "02", "03", "04"]')[
                "مقدار آیتم"].sum()
            Address_Area = df[df["نوع آیتم"] == "ریزآیتمی"].iloc[0]["مساحت آدرس"]
            Spot_Class = df.iloc[0]["نوع لکه"]
            Tree_Area = Address_Area / Independent_Tree
            if Spot_Class in ['07', '08', '09', '10', '11', '12', '13']:
                tree_area = 9 if Tree_Area > 9 else Tree_Area

            for i in TI_Index:
                df.loc[i, "مقدار آیتم"] = df.loc[i, "مقدار آیتم"] * tree_area

            tmp = df.iloc[[0], :]
            tmp.loc[0, "نوع قلم"] = "07"
            tmp.loc[0, "زیرمجموعه هر قلم"] = "09"
            tmp.loc[0, "شناسه"] = (tmp.loc[0, "منطقه"] + "." + tmp.loc[0, "ناحیه"] + "." + tmp.loc[0, "پیمان"] + "."
                                   + tmp.loc[0, "آدرس"] + "." + tmp.loc[0, "نوع لکه"] + "-" + tmp.loc[
                                       0, "نوع قلم"] + "." + tmp.loc[0, "زیرمجموعه هر قلم"])
            tmp.loc[0, "مقدار آیتم"] = Independent_Tree
            tmp.loc[0, "مقدار آیتم خام"] = Independent_Tree
            tmp.loc[0, "نام نوع قلم"] = "درخت و درختچه"
            tmp.loc[0, "نام زیرمجموعه هر قلم"] = "اصله مستقل"
            tmp.loc[0, "نوع آیتم"] = "ریزآیتمی"
            tmp.loc[0, "مساحت آدرس"] = df[df["نوع آیتم"] == "ریزآیتمی"].iloc[0]["مساحت آدرس"]
            tmp.loc[0, "مساحت پیمان"] = df[df["نوع آیتم"] == "ریزآیتمی"].iloc[0]["مساحت پیمان"]

            df = pd.concat([df, tmp])
            result = pd.concat([result, df])
        else:
            result = pd.concat([result, df])

    result = result.reset_index(drop=True)

    return result


def report_area(data):

    tmp1 = data.pivot_table(
        values=["مقدار آیتم"],
        index=["منطقه", "ناحیه", "پیمان", "آدرس"],
        columns=["نام نوع قلم", "نام زیرمجموعه هر قلم"],
        aggfunc={'مقدار آیتم': np.sum}
    )

    tmp2 = data.pivot_table(
        values=["مساحت آدرس"],
        index=["منطقه", "ناحیه", "پیمان", "آدرس"],
        columns=["نوع آیتم"],
        aggfunc={'مساحت آدرس': np.mean}
    )

    tmp = pd.merge(
        left=tmp1.fillna(0),
        right=tmp2.fillna(0),
        how="outer",
        left_index=True,
        right_index=True
    )

    tmp.columns = [x.replace('مقدار آیتم', '').rstrip().lstrip() for x in [' '.join(x) for x in tmp.columns.tolist()]]

    tmp = pd.merge(
        left=tmp,
        right=pd.DataFrame(data.groupby(["منطقه", "ناحیه", "پیمان", "آدرس", "نام نوع لکه", "نام لکه"]).size()).reset_index().drop(columns=[0]).set_index(["منطقه", "ناحیه", "پیمان", "آدرس"]),
        how="outer",
        left_index=True,
        right_index=True
    )

    tmp["مجموع سطوح غیر سبز"] = tmp["آبنما نظافت متر مربع"] + tmp["فضاهاي مسقف متر مربع"] + tmp["محوطه بازي كودكان متر مربع"] + tmp["معابر متر مربع"]
    tmp["مجموع سطوح سبز به غیر از درخت و درختچه"] = tmp["پرچین متر مربع"] + tmp["چمن متر مربع"] + tmp["گل دائم باغچه های معمولی متر مربع"] + tmp["گل دائم فلاورباکسهای سطوح شیب دار متر مربع"] + tmp["گل فصل باغچه های معمولی متر مربع"] + tmp["گل فصل فلاورباکس های سطوح شیب دار متر مربع"]
    tmp["مجموع سطوح"] = tmp["مجموع سطوح غیر سبز"] + tmp["مجموع سطوح سبز به غیر از درخت و درختچه"] + tmp["درخت و درختچه متر مربع"]
    tmp["مجموع سطوح آبیاری تانکری"] = tmp[[col for col in tmp.columns if 'تانکری' in col]].sum(axis=1)
    tmp["مجموع سطوح آبیاری تحت فشار"] = tmp[[col for col in tmp.columns if 'تحت فشار' in col]].sum(axis=1)
    tmp["مجموع سطوح آبیاری ثقلی"] = tmp[[col for col in tmp.columns if 'ثقلی' in col]].sum(axis=1)
    tmp["مجموع سطوح آبیاری شلنگی"] = tmp[[col for col in tmp.columns if 'شلنگی' in col]].sum(axis=1)
    tmp["مجموع کل مساحت تحت آبیاری"] = tmp["مجموع سطوح آبیاری تانکری"] + tmp["مجموع سطوح آبیاری تحت فشار"] + tmp["مجموع سطوح آبیاری شلنگی"] + tmp["مجموع سطوح آبیاری ثقلی"]
    return tmp


















